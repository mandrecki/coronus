
import dash

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css', 'https://fonts.googleapis.com/css?family=Nova+Slim|Raleway&display=swap']
external_scripts = [
    {'src': 'https://www.googletagmanager.com/gtag/js?id=UA-161352689-1', 'async': True},
    {'src': 'https://code.jquery.com/jquery-3.4.1.slim.min.js', 'integrity': 'sha256-pasqAKBDmFT4eHoN2ndd6lN370kFiGUFyTiUHWhU7k8=', 'crossorigin': "anonymous"}
]
dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, meta_tags=[{
      'name': 'viewport',
      'content': 'width=device-width, initial-scale=1.0'
    }])
dash_app.config.suppress_callback_exceptions = True

