from django.shortcuts import render, HttpResponse


# Create your views here.


def welcome(request):
    import pandas as pd
    from mysql import connector
    conn = connector.connect(host="localhost",
                                      user="root",
                                      password='2123@Mysql',
                                      database='fst')
    
    c = conn.cursor()
    
    c.execute("select * from question_bank ORDER BY RAND() limit 5")
    records = c.fetchall()
    global df
    df = pd.DataFrame(records)
    names = [description[0] for description in c.description]
    df.columns = names
    global questions
    questions = df['question']
    
    

    v = df[['question','option1', 'option2', 'option3','option4']]


    return render(request, "samp.html", {"questions":questions, 'options': v.values})


def validate(request):
    if request.method == 'POST':
        co = []
        qidcol = []
        for i in questions:
            co.append(request.POST.get(i))
        #     print("cceexx")
        #     c.execute("select qid from fst.question_bank where question = '{}'".format(i))
        #     r = c.fetchone()[0]
        #     qidcol.append(r)
        cnt = 0
        for i, j in zip(co, list(df['correct_option'])):
            if i == j:
                cnt = cnt + 1
        todb(df['qid'],1, co)
        msg = "Response recorded sucessfully"
    return render(request, 'submit.html', {'msg': msg, 'score': cnt})

def todb( qidcol,sid, attempted):
    import pandas as pd
    from mysql import connector
    conn = connector.connect(host="localhost",
                                      user="root",
                                      password='2123@Mysql',
                                      database='fst')
    
    c = conn.cursor()
    p = pd.DataFrame(zip(qidcol,[sid for j in qidcol], attempted), columns=[ "Question ID","Sid", "Attempted Answer"])
    for i in p.index:
        d = p.iloc[i, [0,1,2]]
        try:
            sq = "Insert into attempt(qid, sid, submission_date, attempted_ans) values ({}, {}, now(), '{}')".format(d[0],d[1], d[2])
            c.execute(sq)
        except connector.IntegrityError:
            print("Integrity Error")
            # sq = "Insert into attempt(qid, sid, submission_date, attempted_ans) values({qid}, {sid}, now(), '{atans}') ON DUPLICATE KEY UPDATE qid = VALUES({qid}) and sid = VALUES({sid})".format(qid = d[0], sid = d[1], atans = d[2])
            # sq = "INSERT INTO attempt (qid, sid, submission_date, attempted_ans) VALUES (2, 1, NOW(), 'neww') AS new_attempt ON DUPLICATE KEY UPDATE submission_date = new_attempt.submission_date, attempted_ans = new_attempt.attempted_ans;"
            sq = "UPDATE attempt SET submission_date = now(), attempted_ans = '{atans}' WHERE qid = {qid} and sid = {sid}".format(qid = d[0], sid = d[1], atans = d[2])
            c.execute(sq)
        finally:
            conn.commit()
    
    conn.close()


