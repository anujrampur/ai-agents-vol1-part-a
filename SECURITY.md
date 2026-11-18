# Security

This repository contains **teaching programs** and invented sample data. It is not meant for production use.

## Please never share secrets

- The Telegram bot in Agent 25 reads its token from the environment variable `TELEGRAM_BOT_TOKEN`. **Never put a token, password or key in a file of this repository, in an issue or in a pull request.**
- If you ever show a token by accident, replace it at once with the service that gave it to you.

## Reporting a security concern

If you find a problem that could put a reader at risk (for example a program that could delete or send data by mistake), please do **not** post details in a public issue. Write to **anujrampur@gmail.com** instead, and describe what you found and how to repeat it.

## Safe use

- Try the programs that change files (Agents 16, 19, 20) on the practice folders first.
- The email and chat agents only write drafts. They never send email by themselves.
- Use sample data while you learn.
