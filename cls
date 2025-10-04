[1mdiff --git a/README.md b/README.md[m
[1mindex 552fdeb..f31acc1 100644[m
[1m--- a/README.md[m
[1m+++ b/README.md[m
[36m@@ -12,40 +12,40 @@[m [mpersonalized-news-anchor/[m
 └── README.md[m
 [m
 [m
[31m-### Fetch general news[m
[32m+[m[32m# Fetch general news[m
 http://127.0.0.1:8000/api/fetch-news/[m
 [m
[31m-### Fetch technology news[m
[32m+[m[32m# Fetch technology news[m
 http://127.0.0.1:8000/api/fetch-news/?category=technology[m
 [m
[31m-### All articles[m
[32m+[m[32m# All articles[m
 http://127.0.0.1:8000/api/articles/[m
 [m
[31m-### Technology articles only[m
[32m+[m[32m# Technology articles only[m
 http://127.0.0.1:8000/api/articles/?category=technology[m
 [m
[31m-### Search for "apple"[m
[32m+[m[32m# Search for "apple"[m
 http://127.0.0.1:8000/api/articles/?search=apple[m
 [m
[31m-### Get Chategories[m
[32m+[m[32m# Get Chategories[m
 http://127.0.0.1:8000/api/categories/[m
 [m
[31m-### Clear news[m
[32m+[m[32m# Clear news[m
 http://127.0.0.1:8000/api/clear-news/[m
 [m
 [m
[31m-### business - Business news[m
[31m-### entertainment - Entertainment news[m
[31m-### general - General news (default)[m
[31m-### health - Health and medical news[m
[31m-### science - Science and research news[m
[31m-### sports - Sports news[m
[31m-### technology - Technology news[m
[32m+[m[32m# business - Business news[m
[32m+[m[32m# entertainment - Entertainment news[m
[32m+[m[32m# general - General news (default)[m
[32m+[m[32m# health - Health and medical news[m
[32m+[m[32m# science - Science and research news[m
[32m+[m[32m# sports - Sports news[m
[32m+[m[32m# technology - Technology news[m
 [m
[31m-### Go to newsapi.org[m
[31m-###Register for a free account[m
[31m-###Get your API key[m
[31m-###Add it to your .env file[m
[32m+[m[32mGo to newsapi.org[m
[32m+[m[32mRegister for a free account[m
[32m+[m[32mGet your API key[m
[32m+[m[32mAdd it to your .env file[m
 [m
[31m-### For starting Application[m
[32m+[m[32m# For starting Application[m
 python manage.py runserver[m
\ No newline at end of file[m
[1mdiff --git a/backend/news_anchor/news/serializers.py b/backend/news_anchor/news/serializers.py[m
[1mindex 4f23dc9..31f40b9 100644[m
[1m--- a/backend/news_anchor/news/serializers.py[m
[1m+++ b/backend/news_anchor/news/serializers.py[m
[36m@@ -1,14 +1,7 @@[m
[31m-# api/serializers.py[m
 from rest_framework import serializers[m
 from .models import NewsArticle[m
[31m-from .summerizer import generate_summary[m
 [m
 class NewsArticleSerializer(serializers.ModelSerializer):[m
[31m-    summary = serializers.SerializerMethodField()[m
[31m-[m
     class Meta:[m
         model = NewsArticle[m
[31m-        fields = "__all__"  # includes title, description, url, source, category, etc.[m
[31m-[m
[31m-    def get_summary(self, obj):[m
[31m-        return generate_summary(obj.description or obj.title)[m
[32m+[m[32m        fields = '__all__'[m
\ No newline at end of file[m
[1mdiff --git a/backend/news_anchor/news/summerizer.py b/backend/news_anchor/news/summerizer.py[m
[1mdeleted file mode 100644[m
[1mindex 8b904c6..0000000[m
[1m--- a/backend/news_anchor/news/summerizer.py[m
[1m+++ /dev/null[m
[36m@@ -1,25 +0,0 @@[m
[31m-# api/summarizer.py[m
[31m-from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer[m
[31m-[m
[31m-MODEL_NAME = "t5-small"[m
[31m-[m
[31m-tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)[m
[31m-model = TFAutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)[m
[31m-[m
[31m-def generate_summary(text, max_len=80, min_len=20):[m
[31m-    if not text:[m
[31m-        return ""[m
[31m-[m
[31m-    input_text = "summarize: " + text[m
[31m-    inputs = tokenizer.encode(input_text, return_tensors="tf", max_length=512, truncation=True)[m
[31m-[m
[31m-    outputs = model.generate([m
[31m-        inputs,[m
[31m-        max_length=max_len,[m
[31m-        min_length=min_len,[m
[31m-        length_penalty=2.0,[m
[31m-        num_beams=4,[m
[31m-        early_stopping=True[m
[31m-    )[m
[31m-[m
[31m-    return tokenizer.decode(outputs[0], skip_special_tokens=True)[m
[1mdiff --git a/backend/news_anchor/news/urls.py b/backend/news_anchor/news/urls.py[m
[1mindex f4c0fbf..8d833ab 100644[m
[1m--- a/backend/news_anchor/news/urls.py[m
[1m+++ b/backend/news_anchor/news/urls.py[m
[36m@@ -15,4 +15,4 @@[m [murlpatterns = [[m
     path('fetch-news/', FetchNewsAPIView.as_view(), name='fetch-news'),[m
     path('categories/', CategoryListView.as_view(), name='categories'),[m
     path('clear-news/', ClearNewsAPIView.as_view(), name='clear-news'),[m
[31m-][m
[32m+[m[32m][m
\ No newline at end of file[m
[1mdiff --git a/personalized-news-anchor b/personalized-news-anchor[m
[1mdeleted file mode 160000[m
[1mindex 2f0a21a..0000000[m
[1m--- a/personalized-news-anchor[m
[1m+++ /dev/null[m
[36m@@ -1 +0,0 @@[m
[31m-Subproject commit 2f0a21a147526066a56b80fd60ecad161dafdeb2[m
