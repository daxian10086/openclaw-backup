#!/bin/bash
# 保存当前会话到MemPalace
mempalace mine "$1" --mode convos --wing openclaw_session
# 更新关键事实层
mempalace wake-up --wing openclaw_session > ~/.openclaw/critical_facts.txt
