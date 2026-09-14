"""Frozen signals in a prospective research journal. No orders or strategy tuning."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
# Isolated calendar dependency; original frozen requirements remain unchanged.
if (ROOT / '.engine_dependencies').exists():
    sys.path.append(str(ROOT / '.engine_dependencies'))
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import uuid
import numpy as np
import pandas as pd
import exchange_calendars as xcals
from . import config
from .data import adjust_ohlc, validate_frame
from .signals import generate_signals
from .runtime_sectors import fetch_sectors
from .release_integrity import verify_runtime

NOTICE = ('RESEARCH SIGNALS ONLY - not investment recommendations. No strategy was validated. '
          'V0/V1 failed to demonstrate a robust edge historically. This journal collects new out-of-sample evidence.')
FEATURES = ['Close','SMA10','SMA20','prior_SMA10','prior_SMA20','ATR14','ATR_pct',
            'prior20_max_ATR_pct','ATR_contraction_threshold','V0','V1']
SCAN = ['ticker','market_data_date','latest_data_date',*FEATURES,'sector','data_status','run_datetime']
JOURNAL = ['signal_id','run_datetime','market_data_date','ticker','sector','signal_type','record_class',
           *FEATURES,'source_snapshot','spec_sha256','engine_sha256','entry_date','entry_price','spy_entry_price',
           'entry_observed_at','outcome_status','exit_date','exit_price','spy_exit_price',
           'valuation_entry_price','valuation_spy_entry_price','stock_return','spy_return','excess_return',
           'outcome_observed_at','outcome_snapshot','price_source','entry_price_source']

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stamp(): return pd.Timestamp.now(tz='UTC')
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def atomic_csv(path, rows, columns):
    temp=path.with_suffix('.tmp')
    pd.DataFrame(rows,columns=columns).to_csv(temp,index=False,float_format='%.17g')
    os.replace(temp,path)

def initialize(out):
    out.mkdir(parents=True,exist_ok=True)
    for name,columns in [('current_signal_scan.csv',SCAN),('current_signals_only.csv',SCAN),('prospective_signal_journal.csv',JOURNAL)]:
        if not (out/name).exists(): atomic_csv(out/name,[],columns)

def load_ledger(path):
    records={}; head='0'*64
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            expected=hashlib.sha256((head+canonical(event['payload'])).encode()).hexdigest()
            if event['previous']!=head or event['hash']!=expected: raise ValueError('Journal integrity failure')
            payload=event['payload']; key=payload['signal_id']; kind=payload['kind']
            if kind=='SIGNAL':
                if key in records: raise ValueError('Duplicate original signal')
                records[key]=payload['values'].copy()
            else:
                if key not in records or records[key]['outcome_status']=='COMPLETE': raise ValueError('Invalid journal transition')
                allowed=({'entry_date','entry_price','spy_entry_price','entry_observed_at','entry_price_source'} if kind=='ENTRY' else
                         {'outcome_status','exit_date','exit_price','spy_exit_price','valuation_entry_price','valuation_spy_entry_price','stock_return','spy_return','excess_return','outcome_observed_at','outcome_snapshot'} if kind=='COMPLETE' else set())
                if not allowed or not set(payload['values']).issubset(allowed): raise ValueError('Attempt to rewrite signal features')
                if kind=='ENTRY' and records[key].get('entry_date'): raise ValueError('Entry already recorded')
                if kind=='COMPLETE' and not records[key].get('entry_date'): raise ValueError('Missing original entry record')
                records[key].update(payload['values'])
            head=event['hash']
    return records,head

def append_event(path, head, kind, key, values):
    payload={'kind':kind,'signal_id':key,'values':values}
    h=hashlib.sha256((head+canonical(payload)).encode()).hexdigest()
    with path.open('a',encoding='utf-8') as f:
        f.write(canonical({'previous':head,'hash':h,'payload':payload})+'\n');f.flush();os.fsync(f.fileno())
    return h

def calendar(now):
    return xcals.get_calendar('XNYS',start=config.HISTORY_START,end=str((now+pd.Timedelta(days=60)).date()))

def latest_closed(cal, now):
    done=cal.schedule[cal.schedule['close']<=now]
    if done.empty: raise ValueError('No completed market session')
    return done.index[-1]

def scan_frames(raws, target, cal, now, sectors):
    sessions=cal.sessions_in_range(cal.first_session,target)
    scans=[]; adjusted={}; audits={}
    for ticker in [*config.UNIVERSE,config.BENCHMARK]:
        raw=raws.get(ticker)
        row={'ticker':ticker,'market_data_date':str(target.date()),'latest_data_date':'','sector':sectors.get(ticker,''),
             'data_status':'DOWNLOAD_FAILED','run_datetime':now.isoformat()}
        if raw is not None and not raw.empty:
            raw=raw.copy();raw.index=pd.DatetimeIndex(raw.index).tz_localize(None).normalize();raw.index.name='Date'
            raw=raw.loc[raw.index<=target]
            row['latest_data_date']=str(raw.index.max().date()) if len(raw) else ''
            if raw.index.duplicated().any():
                audits[ticker]={'error':'duplicate_dates'}
            else:
                quality=validate_frame(raw,sessions)
                factor=raw['Adj Close']/raw.Close
                invalid=set(quality['invalid_dates'])|set(str(d.date()) for d in raw.index[~np.isfinite(factor)|(factor<=0)])
                a=adjust_ohlc(raw).reindex(sessions)
                if invalid: a.loc[a.index.isin(pd.to_datetime(list(invalid))),['Open','High','Low','Close']]=np.nan
                audits[ticker]={**quality,'invalid_adjustment_or_bar_dates':sorted(invalid),'anomaly_policy':'QUARANTINE_NO_REPAIR'}
                adjusted[ticker]=a
                if ticker!=config.BENCHMARK:
                    f=generate_signals(a);x=f.iloc[-1];previous=f.iloc[-2]
                    valid=pd.notna(x.v0) and pd.notna(x.v1)
                    vals=[a.Close.iloc[-1],x.sma10,x.sma20,previous.sma10,previous.sma20,x.atr14,x.atr_pct,x.prior20_atr_pct_max,x.prior20_atr_pct_max*config.CONTRACTION_MULTIPLIER,x.v0,x.v1]
                    row.update({k:(None if pd.isna(v) else bool(v) if k in ['V0','V1'] else float(v)) for k,v in zip(FEATURES,vals)})
                    row['data_status']='OK' if valid else 'UNAVAILABLE'
                    if valid and row['V1'] and not row['V0']: raise AssertionError('V1 is not a subset')
        if ticker!=config.BENCHMARK: scans.append(row)
    return scans,adjusted,audits

def update_journal(out, scans, adjusted, cal, now, snapshot, retrospective=False, price_source='yahoo'):
    ledger=out/'prospective_signal_events.jsonl'
    records,head=load_ledger(ledger);added=completed=0
    for row in scans:
        if row['data_status']!='OK' or not row.get('V0'): continue
        d=pd.Timestamp(row['market_data_date']); entry=cal.session_offset(d,1)
        eligible=(not retrospective and d>pd.Timestamp(config.AS_OF) and now>=cal.session_close(d) and now<cal.session_open(entry))
        for version in ['V0','V1']:
            if not row[version]: continue
            key=f'{d.date()}:{row["ticker"]}:{version}'
            if key in records: continue
            values={k:row[k] for k in ['run_datetime','market_data_date','ticker','sector',*FEATURES]}
            values.update({'signal_id':key,'signal_type':version,'record_class':'PROSPECTIVE' if eligible else 'RETROSPECTIVE',
                           'source_snapshot':snapshot,'spec_sha256':digest(ROOT/'FROZEN_SPECIFICATION.md'),'engine_sha256':digest(__file__),'outcome_status':'PENDING',
                           'price_source':price_source})
            head=append_event(ledger,head,'SIGNAL',key,values);records[key]=values;added+=1
    benchmark=adjusted.get(config.BENCHMARK)
    for key,r in records.items():
        stock=adjusted.get(r['ticker'])
        if r['outcome_status']=='COMPLETE' or stock is None or benchmark is None: continue
        date=pd.Timestamp(r['market_data_date']);entry=cal.session_offset(date,1);exit_=cal.session_offset(date,11)
        # Use only completed daily bars, even for open prices: conservative vendor availability.
        def pair(d):
            if d not in stock.index or d not in benchmark.index or now<cal.session_close(d): return None
            values=[stock.at[d,'Open'],benchmark.at[d,'Open']]
            return [float(x) for x in values] if all(np.isfinite(x) and x>0 for x in values) else None
        ent=pair(entry);end=pair(exit_)
        if ent is not None and not r.get('entry_date'):
            values={'entry_date':str(entry.date()),'entry_price':ent[0],'spy_entry_price':ent[1],'entry_observed_at':now.isoformat(),'entry_price_source':price_source}
            head=append_event(ledger,head,'ENTRY',key,values);r.update(values)
        if ent is not None and end is not None:
            sr=end[0]/ent[0]-1;br=end[1]/ent[1]-1
            values={'outcome_status':'COMPLETE','exit_date':str(exit_.date()),'exit_price':end[0],'spy_exit_price':end[1],
                    'valuation_entry_price':ent[0],'valuation_spy_entry_price':ent[1],'stock_return':sr,'spy_return':br,'excess_return':sr-br,
                    'outcome_observed_at':now.isoformat(),'outcome_snapshot':snapshot}
            head=append_event(ledger,head,'COMPLETE',key,values);r.update(values);completed+=1
    # The CSV is a rebuildable view; original features reside in append-only SIGNAL events.
    records,_=load_ledger(ledger)
    atomic_csv(out/'prospective_signal_journal.csv',records.values(),JOURNAL)
    return added,completed,records

def main(argv=None):
    p=argparse.ArgumentParser(description=NOTICE)
    p.add_argument('--output-dir',type=Path,default=ROOT/'output')
    p.add_argument('--fixture-dir',type=Path,help='Offline replay only; always RETROSPECTIVE')
    p.add_argument('--now',help='UTC replay clock; requires --fixture-dir')
    p.add_argument('--source',choices=['yahoo','moomoo'],default='yahoo',help='Live price source, or the vendor of the bars in --fixture-dir; moomoo uses the hosted Open API after `python -m src.moomoo_login` (see MOOMOO_ADAPTER.md)')
    args=p.parse_args(argv)
    if args.now and not args.fixture_dir: p.error('--now is restricted to offline replay')
    if args.fixture_dir and args.output_dir.resolve()==(ROOT/'output').resolve(): p.error('Offline replay requires a separate --output-dir')
    integrity=verify_runtime();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    lock=out/'.signal_engine.lock'
    try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError: raise RuntimeError('Another run or interrupted run holds .signal_engine.lock; inspect before recovery')
    os.close(fd)
    gateway=None
    try:
        initialize(out)
        if not (out/'prospective_signal_events.jsonl').exists() and len(pd.read_csv(out/'prospective_signal_journal.csv')):
            raise ValueError('Journal ledger missing; restore it before running. Existing CSV will not be replaced.')
        now=pd.Timestamp(args.now) if args.now else stamp()
        if now.tzinfo is None: raise ValueError('Replay clock must include timezone')
        now=now.tz_convert('UTC');cal=calendar(now);target=latest_closed(cal,now)
        if not args.fixture_dir and args.source=='moomoo':
            # Credentials are checked once, before any run artifact exists.
            from .data_moomoo import connect, history as moomoo_history
            gateway=connect();gateway.probe()
        run_id=now.strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]
        snapshot=out/'signal_engine_runs'/run_id;snapshot.mkdir(parents=True)
        raws={};errors={}
        if not args.fixture_dir:
            # yfinance also serves the optional sector lookup, whichever source prices the run.
            import yfinance as yf
            yf.set_tz_cache_location(str(ROOT/'.cache/yfinance'))
        for ticker in [*config.UNIVERSE,config.BENCHMARK]:
            try:
                if args.fixture_dir:
                    frame=pd.read_csv(args.fixture_dir/f'{ticker}.csv',index_col='Date',parse_dates=True)
                elif gateway is not None:
                    frame=moomoo_history(gateway,ticker,config.HISTORY_START,str((target+pd.Timedelta(days=1)).date()))
                else:
                    frame=yf.Ticker(ticker).history(start=config.HISTORY_START,end=str((target+pd.Timedelta(days=1)).date()),**config.DATA_SETTINGS,raise_errors=True,timeout=20)
                if frame.empty: raise ValueError('Empty response')
                frame.to_csv(snapshot/f'{ticker}.csv');raws[ticker]=frame
            except Exception as exc: errors[ticker]=type(exc).__name__+': '+str(exc)
        sectors,sector_audit=fetch_sectors(config.UNIVERSE, offline=bool(args.fixture_dir))
        # Eligibility uses the real post-fetch clock, not a timestamp taken before a slow download.
        recorded=now if args.fixture_dir else stamp()
        scans,adjusted,audits=scan_frames(raws,target,cal,recorded,sectors)
        atomic_csv(snapshot/'scan.csv',scans,SCAN)
        atomic_csv(out/'current_signal_scan.csv',scans,SCAN)
        signals=[r for r in scans if r.get('V0') is True]
        atomic_csv(out/'current_signals_only.csv',signals,SCAN)
        price_source=f'fixture:{args.source}' if args.fixture_dir else args.source
        added,completed,records=update_journal(out,scans,adjusted,cal,recorded,str(snapshot.relative_to(out)),bool(args.fixture_dir),price_source)
        manifest={'run_datetime':recorded.isoformat(),'target_market_date':str(target.date()),'mode':'OFFLINE_RETROSPECTIVE' if args.fixture_dir else 'LIVE',
                  'price_source':price_source,**({'adapter_sha256':digest(ROOT/'src/data_moomoo.py')} if gateway is not None else {}),
                  'sector_metadata':sector_audit,'calendar_version':xcals.__version__,'errors':errors,'quality':audits,'added_records':added,'completed_records':completed,
                  'source_hashes':{x.name:digest(x) for x in snapshot.glob('*.csv')},'engine_sha256':digest(__file__),'spec_sha256':digest(ROOT/'FROZEN_SPECIFICATION.md')}
        (snapshot/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        verify_runtime()
        if integrity['missing_archive_files']:
            print('Public checkout: frozen methodology verified; original vendor archive is not present.')
        unavailable=sum(v=='UNAVAILABLE' for v in sectors.values())
        if unavailable: print(f'Sector metadata unavailable for {unavailable}/50 stocks; signal calculation unaffected.')
        anomalies=sum(len(a.get('invalid_adjustment_or_bar_dates',[])) for a in audits.values())
        if anomalies: print(f'Quarantined {anomalies} invalid bars; see manifest. No historical correction applied.')
        print(NOTICE)
        print(f'Market date {target.date()} | usable {sum(r["data_status"]=="OK" for r in scans)}/50 | V0 {len(signals)} | V1 {sum(r.get("V1") is True for r in signals)}')
        print(f'Journal: {added} new version records, {completed} completed; prospective {sum(r["record_class"]=="PROSPECTIVE" for r in records.values())}.')
        print(f'Outputs: {out}')
        if errors or any(r['data_status']!='OK' for r in scans):
            print('CAUTION: incomplete scan; inspect data_status and run manifest. Unavailable is not FALSE.')
            return 2
        return 0
    finally:
        if gateway is not None: gateway.close()
        lock.unlink()

if __name__=='__main__': sys.exit(main())
