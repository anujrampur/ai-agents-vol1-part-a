# What to run and what to type

Start every agent from the folder that holds all the files. Chat agents end with `quit`. The date in `docs/expected_outputs.txt` is 15 November 2026, so your dates will differ when you run an agent by hand.

## Agent 1 Hello Agent

Run: `python hello_agent.py`

It needs no typing.

## Agent 2 Bill Calculator

Run: `python bill_agent.py`

It needs no typing.

## Agent 3 Weather and Time

Run: `python weather_time_agent.py`

It needs no typing.

## Agent 4 ReAct Reasoning

Run: `python react_agent.py`

It needs no typing.

## Agent 5 Short-Term Memory

Run: `python memory_agent.py` and type:

```
My name is Anuj
My city is Rampur
What is my name?
What is my favourite colour?
history
quit
```

## Agent 6 Note-Taking

Run: `python notes_agent.py` and type:

```
note: Buy chart paper
note: Call the printer about the bill
show notes
find chart
delete note 1
show notes
quit
```

## Agent 7 To-Do and Reminder

Run: `python todo_agent.py` and type:

```
add task Pay the supplier due tomorrow
add task Order chart paper due 2026-11-10
add task Clean the shelf
show tasks
overdue
done 2
show tasks
add task Test due next week
quit
```

## Agent 8 Calendar

Run: `python calendar_agent.py` and type:

```
meeting Supplier visit on tomorrow at 09:00 for 120 minutes
meeting Parent talk on tomorrow at 10:30 for 30 minutes
meeting Parent talk on tomorrow at 11:00 for 30 minutes
show events on tomorrow
free slot on tomorrow for 45 minutes
quit
```

## Agent 9 Converter

Run: `python converter_agent.py` and type:

```
convert 5 km to miles
100 c to f
2 kg in pounds
50 usd to inr
72 f to c
5 km to kg
3 parsec to km
quit
```

## Agent 10 Daily Briefing

First run once: `python seed_demo.py`

Run: `python briefing_agent.py`

It needs no typing.

## Agent 11 Web Search

Run: `python search_agent.py` and type:

```
python lists
how do AI agents save data
sourdough recipes
quit
```

## Agent 12 News Research

Run: `python news_agent.py` and type:

```
load sample_news.xml
news about school
news about school last 3 days
news about cricket
quit
```

## Agent 13 Web Scraping

Run: `python scraper_agent.py` and type:

```
load sample_shop.html
title
headings
links
text
quit
```

## Agent 14 Price Tracker

Run: `python price_agent.py` and type:

```
track gel pens from sample_product.html target 450
check gel pens
```

Then play the shopkeeper: open `sample_product.html`, change `Rs. 499` to `Rs. 459`, save, and run the agent again on another day (or the same day) with:

```
check gel pens
history gel pens
```

## Agent 15 Fact-Checker

Run: `python factcheck_agent.py` and type:

```
The Taj Mahal is in Agra.
The Taj Mahal is in Delhi.
Mount Everest is 7000 metres tall.
Python was created by James Gosling.
Python is a snake.
quit
```

## Agent 16 File Organizer

First run once: `python make_messy_folder.py`

Run: `python organizer_agent.py` and type:

```
scan messy_folder
plan messy_folder
confirm
scan messy_folder
undo
quit
```

## Agent 17 Document Q&A (text and PDF)

Run: `python doc_agent.py` and type:

```
load sample_policy.txt
ask when is the shop open
ask can I return a used notebook
ask do you sell mobile phones
load sample_policy.pdf
ask what is the delivery charge
quit
```

## Agent 18 CSV and Excel Analyst

Run: `python table_agent.py` and type:

```
load sample_sales.csv
describe
sum revenue
average price
revenue by category
top 3 revenue
filter quantity > 25
sum colour
load sample_sales.xlsx
sum revenue
quit
```

## Agent 19 Report Writer

Run: `python report_agent.py` and type:

```
report sample_sales.csv titled Weekly Sales Report
show report
quit
```

## Agent 20 Cleanup and Backup

First run once: `python make_cleanup_practice.py`

Run: `python cleanup_agent.py` and type:

```
duplicates cleanup_practice
large cleanup_practice over 1
old cleanup_practice over 365
plan clean cleanup_practice
confirm
duplicates cleanup_practice
quit
```

## Agent 21 Email Summarizer

First run once: `python make_sample_inbox.py`

Run: `python email_agent.py` and type:

```
load sample_inbox
inbox
digest
summary 7
summary 6
summary 2
quit
```

## Agent 22 Reply Drafting

First run once: `python make_sample_inbox.py`

Run: `python reply_agent.py` and type:

```
load sample_inbox
draft 6 quote formal
draft 3 later short
draft 2 confirm
quit
```

## Agent 23 Meeting Scheduler

First run once: `python make_sample_inbox.py`

Run: `python scheduler_agent.py` and type:

```
load sample_inbox
schedule 4
confirm
book Supplier visit on tuesday at 15:45 for 60 minutes
schedule 1
quit
```

## Agent 24 Shop Support

Run: `python support_agent.py` and type:

```
hello
when is the shop open
order ORD-1001
order ORD-1001 phone 4321
order ORD-1001 phone 0000
do you sell mobile phones
what about quantum computers
you are useless and I am angry
quit
```

## Agent 25 Personal Assistant (practice chat)

Run: `python assistant_bot.py` and type:

```
/help
/note Buy chart paper
/task Pay the supplier due today
/today
/convert 5 km to miles
hello
/dance
quit
```
