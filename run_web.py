import web.jobboard
import config

def run_web():
    web.jobboard.app.run(host='0.0.0.0', port=config.WEB_HTTP_PORT, debug=config.WEB_DEBUG_ENABLED)


if __name__ == '__main__':
    run_web()