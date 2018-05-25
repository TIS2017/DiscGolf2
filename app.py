from flask import Flask, render_template, flash, redirect, url_for, session, request, g
from werkzeug.utils import secure_filename
import controller, helpers, os

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret123'
app._static_folder = 'static'
ctx = app.app_context()
ctx.push()
g.current_division = ''

#-----------------------------------------------------------------------------------------------------------------------

@app.route('/', defaults={'division': ''}, methods=['GET', 'POST'])
@app.route('/<string:division>/', methods=['GET', 'POST'])
def index(division):
    if request.method == 'POST':
        rowsToDisplay = request.form['rows_to_display']
        header, body = controller.getTotalResuls(division, rowsToDisplay)
    else:
        header, body = controller.getTotalResuls(division)
    if division == 'FPO' or division == 'fpo':
        ctx.push()
        g.current_division = 'FPO'
        print('(App) FPO')
    else:
        ctx.push()
        g.current_division = 'MPO'
        print('(App) MPO')

    return render_template('index.html', tableHeader=header, tableBody=body)

@app.route('/tournament', defaults={'id': ''})
@app.route('/tournament/<int:id>/')
def tournament(id):
    print('request: ' + request.path)
    print('(App) Division for tournament: ' + str(g.current_division))
    print('(App) Tournament ID: ' + str(id))
    name, header, body = controller.getTournament(id, g.current_division)

    # print(body)
    return render_template('tournament.html', tournamentName=name, tableHeader=header, tableBody=body)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' not in session:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if controller.login(username, password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('settings'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        return render_template('login.html')
    else:
        return render_template('settings.html')

# Logout
@app.route('/logout')
@helpers.is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Settings
@app.route('/settings', methods=['GET', 'POST'])
@helpers.is_logged_in
def settings():
    settings = controller.getSettings()
    if request.method == 'POST':
        #works
        if request.form['submit'] == 'update_data':
            update_data_day = request.form['update_data_day']
            update_data_time = request.form['update_data_time']
            if update_data_day is not '' and update_data_time is not '':
                controller.setUpdateData(update_data_day, update_data_time)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'hot_rounds_mpo':
            hot_rounds_mpo = request.form['hot_rounds_mpo']
            if hot_rounds_mpo is not '':
                controller.setHotRounds('MPO', hot_rounds_mpo)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'hot_rounds_fpo':
            hot_rounds_fpo = request.form['hot_rounds_fpo']
            if hot_rounds_fpo is not '':
                controller.setHotRounds('FPO', hot_rounds_fpo)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'eligibility_mpo':
            eligibility_mpo = request.form['eligibility_mpo']
            if eligibility_mpo is not '':
                controller.setEligibilityPercentage('MPO', eligibility_mpo)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'eligibility_fpo':
            eligibility_fpo = request.form['eligibility_fpo']
            if eligibility_fpo is not '':
                controller.setEligibilityPercentage('FPO', eligibility_fpo)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'current_year':
            current_year = request.form['current_year']
            if current_year is not '':
                controller.setCurrentYear(current_year)
            else:
                flash('Fill out all fields!', 'danger')

        elif request.form['submit'] == 'tournaments_MPO_FPO':
            tournaments = request.form['tournaments_MPO_FPO']
            if tournaments is not '':
                controller.setTournamentsMPOFPO(tournaments)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'scale_mpo':
            points_scale_MPO_scale = request.form['points_scale_MPO_scale']
            # print(points_scale_MPO_scale)
            points_scale_MPO_points = request.form['points_scale_MPO_points']
            # print(points_scale_MPO_points)
            if points_scale_MPO_scale is not '' and points_scale_MPO_points is not '':
                controller.setPointsScale('MPO', points_scale_MPO_scale, points_scale_MPO_points)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'scale_fpo':
            points_scale_FPO_scale = request.form['points_scale_FPO_scale']
            points_scale_FPO_points = request.form['points_scale_FPO_points']
            if points_scale_FPO_scale is not '' and points_scale_FPO_points is not '':
                controller.setPointsScale('FPO', points_scale_FPO_scale, points_scale_FPO_points)
            else:
                flash('Fill out all fields!', 'danger')

        elif request.form['submit'] == 'tournaments_protour_MPO_FPO':
            tournaments = request.form['tournaments_protour_MPO_FPO']
            if tournaments is not '':
                controller.setTournamentsProTourMPOFPO(tournaments)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'scale_protour_mpo':
            points_scale_protour_MPO_scale = request.form['points_scale_protour_MPO_scale']
            points_scale_protour_MPO_points = request.form['points_scale_protour_MPO_points']
            if points_scale_protour_MPO_scale is not '' and points_scale_protour_MPO_points is not '':
                controller.setPointsScaleProTour('MPO', points_scale_protour_MPO_scale, points_scale_protour_MPO_points)
            else:
                flash('Fill out all fields!', 'danger')
        #works
        elif request.form['submit'] == 'scale_protour_fpo':
            points_scale_protour_FPO_scale = request.form['points_scale_protour_FPO_scale']
            points_scale_protour_FPO_points = request.form['points_scale_protour_FPO_points']
            if points_scale_protour_FPO_scale is not '' and points_scale_protour_FPO_points is not '':
                controller.setPointsScaleProTour('FPO', points_scale_protour_FPO_scale, points_scale_protour_FPO_points)
            else:
                flash('Fill out all fields!', 'danger')

    return render_template('settings.html', settings=settings)

# Save Load - Export Data
@app.route('/downloader', methods=['GET', 'POST'])
def download_file():
    if request.method == 'POST':
        return controller.exportData()
    else:
        return render_template('saveload.html')

# Save Load - Load Data
@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part!', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file!', 'danger')
            return redirect(request.url)
        if file and helpers.allowed_file(file.filename):
            flash('Uploaded!', 'success')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app._static_folder, filename))
            controller.loadData()
            return render_template('saveload.html')
    else:
        return render_template('saveload.html')

# Settings - Wipe Database
@app.route('/wipedatabase', methods=['GET', 'POST'])
def wipe_db():
    if request.method == 'POST':
        if controller.wipeDatabase():
            flash('Completed successfully', 'success')
        else:
            flash('Error occurred!', 'danger')
        return render_template('saveload.html')
    else:
        return render_template('saveload.html')

# Save Load
@app.route('/saveload', methods=['GET', 'POST'])
@helpers.is_logged_in
def saveload():
    return render_template('saveload.html')

# Raw Data
@app.route('/rawdata')
@helpers.is_logged_in
def rawdata():
    return render_template('rawdata.html')

#-----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run()

#-----------------------------------------------------------------------------------------------------------------------

# TODO:
# - Confirmation alerts
# - Update database - screen,logic
# - Select - show selected option
# - Podfarbenie
# - RawData
