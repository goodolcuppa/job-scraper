from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import pandas as pd
import json

from .scraping import reed_url
from .scraping import parse_reed_salaries
from .scraping import scrape_reed_jobs
from .scraping import parse_indeed_salaries
from .scraping import scrape_indeed_jobs
from .scraping import parse_glassdoor_salaries
from .scraping import scrape_glassdoor_jobs

from . import db
from .models import user_job, Job

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    # handle POST requests to views.jobs
    if request.method == 'POST':
        job_role = request.form.get('jobRole')
        job_location = request.form.get('jobLocation')
        return redirect(url_for('views.jobs', job_role=job_role, job_location=job_location))
    
    return render_template('home.html', user=current_user)

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/jobs', methods=['GET', 'POST'])
def jobs():
    # handle POST requests to self
    if request.method == 'POST':
        job_role = request.form.get('jobRole')
        job_location = request.form.get('jobLocation')
        return redirect(url_for('views.jobs', job_role=job_role, job_location=job_location))
    
    # assigning values from GET variables
    job_role = request.args.get('job_role')
    if job_role == '':
        job_role = 'jobs'
    job_location = request.args.get('job_location')
    if job_location == '':
        job_location = None

    # get Indeed data
    indeed_df = scrape_indeed_jobs(job_role, job_location)

    # get Glassdoor data
    glassdoor_df = scrape_glassdoor_jobs(job_role, job_location)

    # get Reed data
    url = reed_url(job_role, job_location)
    reed_df = scrape_reed_jobs(url)

    # create dictionary from uncleaned data
    raw_df = pd.concat([glassdoor_df, indeed_df, reed_df])
    raw_data = raw_df.to_dict('records')

    # clean Indeed data
    indeed_df['salary'] = indeed_df['salary'].apply(parse_indeed_salaries)

    # clean Glassdoor data
    glassdoor_df['salary'] = glassdoor_df['salary'].apply(parse_glassdoor_salaries)

    # clean Reed data
    reed_df['salary'] = reed_df['salary'].apply(parse_reed_salaries)

    # create dictionary from cleaned data
    df = pd.concat([glassdoor_df, indeed_df, reed_df])
    data = raw_df.to_dict('records')
    
    return render_template(
        'jobs.html',
        user = current_user,
        jobs = raw_data,
        job_role = job_role,
        job_location = job_location,
        mean_salary = "{:,}".format(int(df['salary'].mean())),
        unique_companies = len(df.company.unique()),
        unique_roles = len(df.title.unique())
    )

@views.route('/saved')
def saved():
    return render_template(
        'saved.html',
        user = current_user
    )

@views.route('/save-job', methods=['POST'])
def save_job():
    data = json.loads(request.data)
    job = data['job']
    
    if job:
        new_job = Job(
            title=job['title'], 
            company=job['company'], 
            url=job['url'], 
            location=job['location'], 
            salary=job['salary']
        )
        db.session.add(new_job)
        current_user.saved.append(new_job)
        db.session.commit()
        return jsonify({})
    
@views.route('/delete-job', methods=['POST'])
def delete_job():
    data = json.loads(request.data)
    job_id = data['jobId']

    if job_id:
        job = Job.query.get(job_id)
        job.saves.remove(current_user)
        if not job.saves:
            db.session.delete(job)
        db.session.commit()
        return jsonify({})