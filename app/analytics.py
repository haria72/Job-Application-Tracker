from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
# StreamingResponse lets us return a file (like an image) directly from an endpoint
# instead of returning JSON, we return the image bytes as a PNG
import matplotlib.pyplot as plt
import io
# io.BytesIO is an in-memory file — we save the chart here instead of saving it to disk
# then we stream it directly to the client
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
import pandas as pd

analytics_router = APIRouter()

def get_applications_df(db: Session):
    applications = db.query(models.Application).all()
    if not applications:
        return None
    data = [{
        "id": a.id,
        "company": a.company,
        "role": a.role,
        "link": a.link,
        "platform": a.platform,
        "app_type": a.app_type,
        "stage": a.stage,
        "applied_date": a.applied_date,
        "response_date": a.response_date,
        "notes": a.notes
    } for a in applications]
    return pd.DataFrame(data)

#Which platform gets most responses
@analytics_router.get("/analytics/platform")
def platform_analytics(db: Session = Depends(get_db)):
    df = get_applications_df(db)
    if df is None:
        return {"message": "No applications found"}
    total = df.groupby("platform").size().rename("total_applied")
    responded = df[df['stage'] != "applied"].groupby("platform").size().rename("total_responded")
    # pd.concat joins two Series side by side into one DataFrame
    # axis=1 means "join as columns" (side by side)
    # axis=0 would mean "join as rows" (on top of each other)
    # e.g.        total_applied  total_responded
    #  linkedin       10              6
    #  naukri          5              1

    # fillna(0) replaces any NaN (empty) values with 0
    # NaN appears when a platform has applications but zero responses
    # without this, the response_rate calculation would break
    result = pd.concat([total, responded], axis=1).fillna(0)
    result["response_rate"] = ((result["total_responded"] / result["total_applied"]) * 100).round(1) #rounds to 1 decimal place
    # reset_index() promotes "platform" from the index into a regular column
    # without this, platform would be the row label, not a column, and wouldn't show in the output
    # to_dict(orient="records") converts the DataFrame into a list of dicts
    # e.g. [{"platform": "linkedin", "total_applied": 10, "total_responded": 6, "response_rate_%": 60.0}]
    # FastAPI can return a list of dicts directly as JSON
    return result.reset_index().to_dict(orient="records")
    
@analytics_router.get("/analytics/days")
def day_analytics(db: Session = Depends(get_db)):
    df = get_applications_df(db)
    if df is None:
        return {"message": "No applications found"}
    df["applied_day"] = pd.to_datetime(df["applied_date"]).dt.day_name() #extracts the day of the week from the applied_date
    total = df.groupby("applied_day").size().rename("total_applied")
    responded = df[df["response_date"].notna()].copy()

    if not responded.empty:
        responded["applied_day"] = pd.to_datetime(responded["applied_date"]).dt.day_name()
        resp_count = responded.groupby("applied_day").size().rename("total_responded")
    else:
        resp_count = pd.Series(dtype=int, name="total_responded") #empty Series with integer type and name "total_responded"
    
    result = pd.concat([total, resp_count], axis=1).fillna(0)

    result["response_rate"] = ((result["total_responded"] / result["total_applied"]) * 100).round(1)

    return result.reset_index().to_dict(orient="records")

# ─── ENDPOINT 3: RESPONSE TIME ───────────────────────────────────────────────
# answers: how many days does it typically take to hear back?
# also shows fastest and slowest response times

@analytics_router.get("/analytics/response-time")
def response_time(db: Session = Depends(get_db)):
    df = get_applications_df(db)
    if df is None:
        return {"message": "No applications yet"}

    # filter to only rows that have a response_date
    responded = df[df["response_date"].notna()].copy()

    if responded.empty:
        return {"message": "No responses recorded yet — add response dates to your applications"}

    # subtract applied_date from response_date to get the number of days between them
    # pd.to_datetime() converts both columns to datetime first
    # .dt.days extracts the number of days from the resulting timedelta
    # e.g. response_date(2026-05-10) - applied_date(2026-05-01) = 9 days
    responded["days_to_response"] = (
        pd.to_datetime(responded["response_date"]) - pd.to_datetime(responded["applied_date"])
    ).dt.days

    return {
        # .mean() calculates the average of the column
        "average_days_to_response": round(responded["days_to_response"].mean(), 1),

        # .min() gets the smallest value — fastest response
        "fastest_response_days": int(responded["days_to_response"].min()),

        # .max() gets the largest value — slowest response
        "slowest_response_days": int(responded["days_to_response"].max()),

        # len() counts how many rows are in the filtered DataFrame
        "total_responses_recorded": len(responded)
    }

# ─── ENDPOINT 4: WEEKLY SUMMARY ─────────────────────────────────────────────
# answers: full picture — how is my job hunt going overall?
# total applied, response rate, breakdown by stage, platform, and type

@analytics_router.get("/analytics/summary")
def weekly_summary(db: Session = Depends(get_db)):
    df = get_applications_df(db)
    if df is None:
        return {"message": "No applications yet"}
     # len() counts total rows in the DataFrame = total applications sent
    total_applied = len(df)

    # count rows where response_date is not empty = someone responded
    total_responded = len(df[df["response_date"].notna()])

    # calculate overall response rate
    # the "if total_applied > 0" check avoids dividing by zero
    response_rate = round((total_responded / total_applied) * 100, 1) if total_applied > 0 else 0

    # groupby("stage").size() counts how many applications are at each stage
    # .to_dict() converts it to a plain dict — e.g. {"applied": 5, "rejected": 3, "technical": 2}
    stage_breakdown = df.groupby("stage").size().to_dict()

    # same idea for platform — e.g. {"linkedin": 6, "naukri": 4}
    platform_breakdown = df.groupby("platform").size().to_dict()

    # same for app_type — e.g. {"easy": 4, "tailored": 3, "referral": 1}
    app_type_breakdown = df.groupby("app_type").size().to_dict()

    return {
        "total_applied": total_applied,
        "total_responded": total_responded,
        "response_rate_%": response_rate,
        "stage_breakdown": stage_breakdown,
        "platform_breakdown": platform_breakdown,
        "app_type_breakdown": app_type_breakdown
    }
    
@analytics_router.get("/analytics/chart/stages")
def stage_chart(db: Session = Depends(get_db)):
    df = get_applications_df(db)
    if df is None:
        return {"message": "No applications yet"}

    stage_counts = df.groupby("stage").size()

    # create a new figure — like a blank canvas
    # figsize sets the width and height in inches
    fig, ax = plt.subplots(figsize=(6, 5))

    # draw a bar chart
    # stage_counts.index = the stage names (x axis)
    # stage_counts.values = the counts (y axis)
    # color sets the bar colou
    ax.bar(stage_counts.index, stage_counts.values, color="#7F77DD")

    ax.set_xlabel("Stage")
    ax.set_ylabel("Number of Applications")
    ax.set_title("Applications by Stage")

    # rotate x axis labels so they don't overlap
    plt.xticks(rotation=45, ha="right")
    
    # tight_layout automatically adjusts spacing so nothing gets cut off
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0) 
    plt.close() #close the figure to free up memory

    return StreamingResponse(buf, media_type="image/png")