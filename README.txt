Chen ji, N13729440

Design:
The project uses Django Template and is deployed on Google App Engine. 

Address is http://chenji-opensource.appspot.com

The website uses python and Django templates stored in templates/opensource to generate views, it is very straightforward and easy using, it consists of mainly three parts: 

1. main_page: the home page shows a list of the questions. Questions listed in the main_page can be sorted through different ways: by date_create, by votes_number, by views_number, by answer_number. You can sort it simply by clicking the sort tags at top. Also, user can use search, or click on a specific tag to show the questions with the tag only, while questions do not have the tag will not be displayed. The sort and search results are paged for every 10 results. You can click next button to show the next 10. There is a "ask question" button at the top right of the page, which by clicking can post new questions; Users can also click the Question title to go to the question_page.

2. question_page: shows detail information of a question (title, content, vote number, answers number, views number, author, date created/modified, etc.) and all the answers of the question(and their votes, content, author, etc.). At the bottom of the quesion_page,  user can post answer to that question. At the left side of the content shows the vote count of a question/answer. Clicking the top and bottom arrows votes up/down to the question&answer. After posting a new answer or giving a new vote, the page will be refreshed and the new answer and value of votes will be displayed. 

There is an rss link at the bottom of this page linking to an rss feed of the question, which contains all the information of the question and its answers.

3. post&edit forms: after clicking ask question button at main_page, or at the bottom of question_page, users can post new questions&answers or edit their own questions&answers. If editing, the original contend will filled by default. Users can also upload pictures by clicking upload. The web browser will open a new window showing your uploaded picture, you can paste the string value beside the picture in the content to display the image in you question&answer. Users without logging in cannot post questions or answers. Only the author of a question/answer can edit it.

4. There are some other little tricks on the website. You may click the "OpenSource" icon at the left side of top-bar to go back to the home page. And you can login/logout any time by clicking the login/logout button at the right side of the top-bar. You can also use admin id to modify database. 
the admin Id is opens.ad.001@gmail.com, password is opensource001


Structure:
1.DB: There are four entities as shown in models.py: Question, Answer (Both subclass of Post), Vote_Question and Vote_Answer.

2.Templates: All Django templates are stored in templates/opensource. main_page shows the home page, form_page and edit_answer shows the from submit page, question_page shows the question, error_page shows error message, admin_page gives admin to manage DataBase.

3.Views: All the website views are generated from views.py. Each function has a short comment in the file describes the usage. Which will not be list here.

4.Templatetags: I write a filter to handle images display.

5.Static: the css file and back-ground pictures are stored there.
