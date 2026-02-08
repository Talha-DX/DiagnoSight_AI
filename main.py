from gui import SplashScreen, MainApp

def launch_main_app():
    MainApp()

if __name__ == "__main__":
    SplashScreen(on_finish_callback=launch_main_app)
    
