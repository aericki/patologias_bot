from dotenv import load_dotenv

from src.config import load_settings, setup_logging
from src.infrastructure.telegram.bot import create_application


def main():
    load_dotenv()
    settings = load_settings()
    setup_logging(settings.log_level)

    app = create_application(settings)
    print("Bot iniciado...")
    app.run_polling(poll_interval=settings.poll_interval)


if __name__ == "__main__":
    main()
