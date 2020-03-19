
import dash

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css', 'https://fonts.googleapis.com/css?family=Nova+Slim|Raleway&display=swap']
dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=[{'src': 'https://www.googletagmanager.com/gtag/js?id=UA-161352689-1', 'async': True}])
dash_app.config.suppress_callback_exceptions = True

