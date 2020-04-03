from flask_setup import app
from engine.utility import *
from cov_backend import cov_calc
from gevent.pywsgi import WSGIServer
from flask import flash, request, redirect, render_template, session
import os
import pandas as pd
import datetime

IP = '127.0.0.1'
PORT = 5000


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':

        # Rendering the index page
        return render_template('index.html')

    if request.method == 'POST':

        if request.form.getlist('check'):

            # Agreed terms
            session['agree'] = True

            # Go the the next page
            return redirect('/input')

        else:
            # Error if terms are not agreed
            return err('/', 'You need to agree the terms and conditions.')


@app.route('/estimate_infection_rate', methods=['POST', 'GET'])
def estimate():

    if request.method == 'GET':

        # Check agreed terms
        if 'agree' in session:

            # No calculation first
            di = ''

            # Rendering the page first time
            return render_template('estimate_infection_rate.html',
                                   di=di, ep=['', '', ''])

        else:

            # Error if terms are not agreed
            return err('/', 'You need to agree the terms and conditions.')

    if request.method == 'POST':

        try:
            N = int(request.form['e1'])
            Ni = int(request.form['e2'])
            t = int(request.form['e3'])

        # Error if string conversion fails
        except ValueError:

            # Redirect to the same page if type conversion fails
            return err(request.url, 'Only numbers are allowed as input!')

        try:
            # Estimate daily infection rate
            di = daily_infection_rate(N, Ni, t)

        # Error if string conversion fails
        except ArithmeticError:

            # Redirect to the same page if type conversion fails
            return err(request.url, 'Arithmetic Error Occurred.')

        # Redirect to next input page
        return render_template('estimate_infection_rate.html',
                               di=di, ep=[N, Ni, t])


@app.route('/input', methods=['POST', 'GET'])
def input():
    '''2nd page on the frontend, providing the describing statistics,
    the histogram and the input parameter reader.

    Args:
        None

    Returns:
       Flask redirection, depending on sucessfull uploading. Otherwise error.

    '''

    if request.method == 'GET':

        # Check agreed terms
        if 'agree' in session:

            # Rendering the page first time
            return render_template('input.html')

        else:

            # Error if terms are not agreed
            return err('/', 'You need to agree the terms and conditions.')

    if request.method == 'POST':

        # Generate labels for the parameter list
        par_list = ['par' + str(x) for x in range(1, 5)]

        # Convert parameters from string to float if possible,FIST 5 PARAMETERS
        try:
            session['parameters'] = [float(request.form[x]) for x in par_list]

        # Error if string conversion fails
        except ValueError:

            # Redirect to the same page if type conversion fails
            return err(request.url, 'Only numbers are allowed as input!')

        # Check optional imput parameters
        a = request.form['opt1'] == 'None'
        b = request.form['opt2'] == 'None'

        # Check optional parameters: WITHOUT OPTIONAL PARAMETERS
        if a and b:

            # Optional parameters are not set
            session['optional1'] = None
            session['optional2'] = None

        # Check optional parameters: ONLY ONE OPTIONAL PARAMETER - ERROR
        elif (a and not b) or (not a and b):

            # Error message
            return err(request.url, 'Both optional parameters must be set!')

        # Check optional parameters: BOTH OPTINAL PARAMETER SET
        elif (not a) and (not b):

            try:
                session['optional1'] = int(request.form['opt1'])
                session['optional2'] = int(request.form['opt2'])

            # Error if string conversion fails
            except ValueError:

                # Error message
                return err(request.url, 'Optional parameters must be numbers!')

            if (session['optional1'] > session['parameters'][2]):

                # Error message
                return err(request.url,
                           'Critical Area must be <= Number of Area')

            if (session['optional1'] < 1):
                # Error message
                return err(request.url, 'Critical Area must be >=1')

        else:

            # Error message
            return err(request.url, 'Unkown error occured!')

    # Redirect to next input page
    return redirect('/input2')


@app.route('/input2', methods=['POST', 'GET'])
def input2():

    if request.method == 'GET':

        # Check agreed terms
        if 'agree' in session:

            # Check nG lenght
            nG = int(session['parameters'][2])

            # Create a matrix form for the area parameters
            par_area = parameter_matrix(nG)

            return render_template('input2.html',
                                   par_area=par_area,
                                   par=session['parameters'],
                                   opt1=session['optional1'],
                                   opt2=session['optional2'])

        else:

            # Error message
            return err('/', 'You must accept the terms and conditions.')

    if request.method == 'POST':

        # Lenght of input parameters
        nG = int(session['parameters'][2])

        try:

            # Convert input to integers
            IR = [int(request.form['IR' + str(x)]) for x in range(1, nG + 1)]
            DO = [int(request.form['DO' + str(x)]) for x in range(1, nG + 1)]

            # Store the area input values as a session
            session['IR'] = IR
            session['DO'] = DO

        # Error if string conversion fails
        except ValueError:

            # Error message
            return err(request.url, 'Area parameters must be numbers!')

        # Redirect to next input page
        return redirect('/output')


@app.route('/output', methods=['POST', 'GET'])
def output():
    '''Output page for the fontend, providing the results of the vcdn
    calculations.

    Args:
        None

    Returns:
       Flask redirection, depending on sucessfull uploading. Otherwise error.

    '''

    if request.method == 'GET':

        # Check agreed terms
        if 'agree' in session:

            try:

                # Optional parameters not set
                if not session['optional1']:

                    # Label of critical area
                    ca = False

                    # Value of critical area
                    cn = False

                    # Call the model
                    d, t, tc, = cov_calc(session['parameters'],
                                         session['IR'],
                                         session['DO'],
                                         session['optional1'],
                                         session['optional2'])

                    # Create the first total plots
                    su, div = plot_total(d, t, panel=False, diff=False)

                    # Create the area plots
                    su2, div2 = plot_total_col(d, tc, ca, cn,
                                               panel=False, diff=False)

                # Optional parametes set
                else:

                    # Label of critical area
                    ca = str(session['optional1'])

                    # Value of critical area
                    cn = str(session['optional2'])

                    # Call the model
                    d, t, tc = cov_calc(session['parameters'],
                                        session['IR'],
                                        session['DO'],
                                        session['optional1'],
                                        session['optional2'])

                    # Create the first total plots
                    su, div = plot_total(d, t, panel=True, diff=False)

                    # Create the area plots
                    su2, div2 = plot_total_col(d, tc, ca, cn,
                                               panel=True, diff=False)

                return render_template('output.html',
                                       output_script=su,
                                       output_div=div,
                                       output_script_g=su2,
                                       output_div_g=div2)

            except KeyboardInterrupt as e:

                # Error message
                errorm = 'An error occurred while processing your request: '
                flash(errorm + str(e))

                # Return to the parameter page
                return redirect('/input2')

        else:

            flash('You must accept the terms and conditions.')

            return redirect('/')

    if request.method == 'POST':

        if request.form['share'] == 'Share Parameters':

            # Confirm message to the front end
            return redirect('/share_input')


@app.route('/share_input', methods=['POST', 'GET'])
def share_input():

    if request.method == 'GET':

        # Go to the share input site
        return render_template('share_input.html')

    if request.method == 'POST':

        # Read additional information
        session['dep_type'] = str(request.form['dep_type'])

        # Record date
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        session['date'] = date

        # Save notes
        session['notes'] = str(request.form['notes'])

        # Record survey if taken
        survey = {'Date': [session['date']],
                  'Appearance': [request.form['Appearance']],
                  'Usability': [request.form['Usability']],
                  'Usefulness': [request.form['usefulness']],
                  'Comment': [request.form['comment_review']]}

        # Write the answer in a file
        filled = save_survey(survey)

        # Save or updata paramater file
        saved = update_par(session)

        if not saved:

            # Error message
            return err(request.url, 'Unknown error occurred.!')

        else:

            # Go to the next page
            return redirect('/share')


@app.route('/share', methods=['POST', 'GET'])
def share():

    if request.method == 'GET':

        # Read csv data from file
        table = pd.read_csv('pub/shared_par.csv', index_col=0)

        # Convert dataframe to html
        table_html = table.to_html(index=False, justify='left')

        return render_template('share.html', table_html=table_html)


@app.route('/docs', methods=['GET'])
def docs():
    if request.method == 'GET':

        # Rendering the index page
        return render_template('docs.html')


if __name__ == "__main__":

    app.run(debug=True)
    # Use gevent WSGI server and start the server
    #WSGIServer((IP, PORT), app.wsgi_app).serve_forever()
