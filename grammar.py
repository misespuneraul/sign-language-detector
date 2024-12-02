import language_tool_python

text = "caR"
tool = language_tool_python.LanguageTool('en-US')
result = tool.correct(text)
print(result)