interface TelegramWebApp {
  ready(): void;
  expand(): void;
  close(): void;
  sendData(data: string): void;
  disableVerticalSwipes(): void;
}

interface Window {
  Telegram: {
    WebApp: TelegramWebApp;
  };
}

declare const Telegram: {
  WebApp: TelegramWebApp;
};
