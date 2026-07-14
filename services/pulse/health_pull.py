import json,urllib.request,urllib.parse,datetime,os,subprocess
def ef(p):
 d={}
 for l in open(p):
  l=l.strip()
  if "=" in l and l[:1]!="#":k,v=l.split("=",1);d[k]=v.strip().strip('"').strip("'")
 return d
S=ef("/root/.secrets/google_health.env");V=ef("/root/.secrets/vitrina_db.env");T=json.load(open("/root/.secrets/google_health_tokens.json"))
q=urllib.parse.urlencode({"refresh_token":T["refresh_token"],"client_id":S["GOOGLE_HEALTH_CLIENT_ID"],"client_secret":S["GOOGLE_HEALTH_CLIENT_SECRET"],"grant_type":"refresh_token"}).encode()
nt=json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token",data=q,timeout=30));AT=nt["access_token"]
nt.setdefault("refresh_token",T["refresh_token"]);os.umask(0o077);json.dump(nt,open("/root/.secrets/google_health_tokens.json","w"))
B="https://health.googleapis.com/v4/users/me/dataTypes/"
def api(u,b=None):
 h={"Authorization":"Bearer "+AT}
 if b is not None:h["Content-Type"]="application/json";b=json.dumps(b).encode()
 try:return json.load(urllib.request.urlopen(urllib.request.Request(u,data=b,headers=h),timeout=45))
 except Exception:return {}
def F(x):
 try:return float(x)
 except Exception:return None
D=datetime.datetime.utcnow()+datetime.timedelta(hours=4);a=D.date()-datetime.timedelta(days=2);b=D.date()+datetime.timedelta(days=1)
if os.environ.get("HP_START"): a=datetime.date.fromisoformat(os.environ["HP_START"])
if os.environ.get("HP_END"): b=datetime.date.fromisoformat(os.environ["HP_END"])
def dk(dd):return "%04d-%02d-%02d"%(dd.get("year",0),dd.get("month",0),dd.get("day",1)) if isinstance(dd,dict) else None
def roll(dt):
 r=api(B+dt+"/dataPoints:dailyRollUp",{"range":{"start":{"date":{"year":a.year,"month":a.month,"day":a.day},"time":{"hours":0}},"end":{"date":{"year":b.year,"month":b.month,"day":b.day},"time":{"hours":0}}},"windowSizeDays":1})
 o={}
 for p in (r.get("rollupDataPoints",[]) if isinstance(r,dict) else []):
  k=dk(p.get("civilStartTime",{}).get("date"))
  if k:o[k]=p
 return o
def dl(dt,f):
 r=api(B+dt+'/dataPoints?pageSize=31&filter='+urllib.parse.quote(f+'.date >= "'+a.isoformat()+'" AND '+f+'.date < "'+b.isoformat()+'"'))
 o={}
 cc=dt.split("-");kk=cc[0]+"".join(w.capitalize() for w in cc[1:])
 for p in (r.get("dataPoints",[]) if isinstance(r,dict) else []):
  ob=p.get(kk,p);k=dk(ob.get("date"))
  if k:o[k]=ob
 return o
def sl():
 r=api(B+'sleep/dataPoints?pageSize=25&filter='+urllib.parse.quote('sleep.interval.end_time >= "'+a.isoformat()+'T00:00:00Z" AND sleep.interval.end_time < "'+b.isoformat()+'T00:00:00Z"'))
 o={}
 for p in (r.get("dataPoints",[]) if isinstance(r,dict) else []):
  s=p.get("sleep",p);iv=s.get("interval",{});k=str(iv.get("endTime") or iv.get("civilEndTime") or "")[:10]
  if k and not (s.get("metadata",{}) or {}).get("nap"):o[k]=s
 return o
st=roll("steps");di=roll("distance");fl=roll("floors");hr=roll("heart-rate");am=roll("active-minutes");az=roll("active-zone-minutes");ae=roll("active-energy-burned");tc=roll("total-calories")
rh=dl("daily-resting-heart-rate","daily_resting_heart_rate");hv=dl("daily-heart-rate-variability","daily_heart_rate_variability");sp=dl("daily-oxygen-saturation","daily_oxygen_saturation");rr=dl("daily-respiratory-rate","daily_respiratory_rate");sm=sl()
def g(m,d,*p):
 x=m.get(d)
 for s in p:x=x.get(s) if isinstance(x,dict) else None
 return F(x)
def sc(m,d,*c):
 o=m.get(d)
 if isinstance(o,dict):
  for k in c:
   if F(o.get(k)) is not None:return F(o.get(k))
 return None
def N(v):return "NULL" if v is None else (str(int(v)) if float(v).is_integer() else str(round(v,2)))
def Q(v):return "NULL" if not v else "'"+str(v).replace("'","''")+"'"
days=sorted(set(list(st)+list(di)+list(fl)+list(hr)+list(am)+list(az)+list(ae)+list(tc)+list(rh)+list(hv)+list(sp)+list(rr)+list(sm)))
cols="metric_date,source,steps,distance_km,floors,active_minutes,active_zone_minutes,active_kcal,total_kcal,hr_avg,hr_min,hr_max,resting_hr,hrv_ms,spo2_avg,respiratory_rate,sleep_total_min,sleep_deep_min,sleep_rem_min,sleep_light_min,sleep_awake_min,sleep_start,sleep_end,sleep_efficiency,raw"
rows=[]
for d in days:
 raw={k:m[d] for k,m in [("steps",st),("distance",di),("floors",fl),("heartRate",hr),("activeMinutes",am),("activeZoneMinutes",az),("activeEnergyBurned",ae),("totalCalories",tc),("restingHeartRate",rh),("hrv",hv),("oxygenSaturation",sp),("respiratoryRate",rr),("sleep",sm)] if m.get(d) is not None}
 dm=g(di,d,"distance","millimetersSum");km=round(dm/1000000.0,2) if dm is not None else None
 amn=None
 if am.get(d):
  ar=(am[d].get("activeMinutes",{}) or {}).get("activeMinutesRollupByActivityLevel") or [];amn=sum(int(x.get("activeMinutesSum",0) or 0) for x in ar) if ar else None
 azm=None
 if az.get(d):
  z=az[d].get("activeZoneMinutes",{}) or {};azm=sum(int(z.get(k,0) or 0) for k in ("sumInCardioHeartZone","sumInPeakHeartZone","sumInFatBurnHeartZone")) if z else None
 s=sm.get(d);su=(s or {}).get("summary",{}) if isinstance(s,dict) else {};iv=(s or {}).get("interval",{}) if isinstance(s,dict) else {}
 sto=F(su.get("minutesAsleep"));spd=F(su.get("minutesInSleepPeriod"))
 def stg(*t):
  tt=0;gg=False
  for x in (su.get("stagesSummary") or []):
   if x.get("type") in t and F(x.get("minutes")) is not None:tt+=F(x.get("minutes"));gg=True
  return int(tt) if gg else None
 eff=int(round(sto/spd*100)) if (sto and spd) else None
 rj=json.dumps(raw,ensure_ascii=False).replace("'","''")
 v=["'"+d+"'","'google_health'",N(g(st,d,"steps","countSum")),N(km),N(g(fl,d,"floors","countSum")),N(amn),N(azm),N(g(ae,d,"activeEnergyBurned","kcalSum")),N(g(tc,d,"totalCalories","kcalSum")),N(g(hr,d,"heartRate","beatsPerMinuteAvg")),N(g(hr,d,"heartRate","beatsPerMinuteMin")),N(g(hr,d,"heartRate","beatsPerMinuteMax")),N(sc(rh,d,"beatsPerMinute")),N(sc(hv,d,"averageHeartRateVariabilityMilliseconds")),N(sc(sp,d,"avgOxygenSaturationPercentage","oxygenSaturationPercentage","averageOxygenSaturationPercentage","percentage")),N(sc(rr,d,"avgBreathsPerMinute","breathsPerMinute","averageBreathsPerMinute")),N(sto),N(stg("DEEP")),N(stg("REM")),N(stg("LIGHT")),N(F(su.get("minutesAwake"))),Q(iv.get("startTime")),Q(iv.get("endTime")),N(eff),"'"+rj+"'::jsonb"]
 rows.append("("+",".join(v)+",now())")
env=os.environ.copy();env.update({"PGHOST":V.get("PGHOST","127.0.0.1"),"PGUSER":V["PGUSER"],"PGDATABASE":V["PGDATABASE"],"PGPASSWORD":V.get("PGPASSWORD","")})
if rows:
 up=",".join("%s=COALESCE(EXCLUDED.%s,pulse.health_daily.%s)"%(c,c,c) for c in cols.split(",")[2:-1])+",raw=EXCLUDED.raw,updated_at=now()"
 sql="INSERT INTO pulse.health_daily("+cols+",updated_at) VALUES "+",".join(rows)+" ON CONFLICT(metric_date) DO UPDATE SET "+up+";"
 p=subprocess.run(["psql","-v","ON_ERROR_STOP=1","-q","-c",sql],env=env,capture_output=True,text=True)
 print("rc",p.returncode,p.stderr[:200])
print(subprocess.run(["psql","-tA","-c","select metric_date,steps,distance_km,floors,active_kcal,resting_hr,sleep_total_min from pulse.health_daily order by metric_date desc limit 5"],env=env,capture_output=True,text=True).stdout)
