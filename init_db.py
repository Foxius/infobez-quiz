from app import app, db, Quiz, Question, Option
import os

with app.app_context():
    if os.path.exists('quiz.db'):
        os.remove('quiz.db')
    db.create_all()

    quiz = Quiz(title="Мемный квиз по инфобезу")
    db.session.add(quiz)
    db.session.commit()

    images = [
        "https://avatars.mds.yandex.net/i?id=b92a0debdd155675f0c3d3a15e3f6a79_l-10096313-images-thumbs&n=13",
        "https://i.ytimg.com/vi/hGiXAGAQquo/maxresdefault.jpg",
        "https://i.pinimg.com/originals/d9/77/23/d9772345fc4c404fcea836303d25152e.jpg",
        "https://avatars.mds.yandex.net/i?id=a24f92fb35c33ed350be826571c631f44b04a8b9-9150622-images-thumbs&n=13",
        "https://avatars.mds.yandex.net/i?id=b0cb35dc966e04b774a95cc60b3c193f_l-7451997-images-thumbs&n=13",
        "https://i.postimg.cc/C1rpRZH6/rotten-fores-stiks-by-fstikbot-agadagadnoedig.png",
        "https://i.postimg.cc/d0vYpcVn/rotten-fores-stiks-by-fstikbot-agadggadnoedig.png",
        "https://i.postimg.cc/gJ2PcyRZ/rotten-fores-stiks-by-fstikbot-agadjwadnoedig.png",
        "https://i.postimg.cc/cJmSNkKW/rotten-fores-stiks-by-fstikbot-agadngadnoedig.png",
        "https://i.postimg.cc/Dy9FQXV9/rotten-fores-stiks-by-fstikbot-agadoaadnoedig.png",
        "https://i.postimg.cc/Sxc4gxkJ/rotten-fores-stiks-by-fstikbot-agadsweaajtngyi.png",
        "https://i.postimg.cc/zXFZhPjg/image.png",
    ]

    questions_data = [
        {
            'text': '«Твой пароль — 123456. Что произойдет?',
            'options': [
                'Ничего, я же не миллионер.',
                'Тебя взломают быстрее, чем ты дочитаешь этот вопрос.',
                'Получишь VIP-доступ к соцсетям.'
            ],
            'correct': 1
        },
        {
            'text': 'Какой пароль самый надежный?',
            'options': [
                'Любовь2007',
                'CorrectHorseBatteryStaple',
                'qwertyuiop'
            ],
            'correct': 1
        },
        {
            'text': 'Тебе пришло SMS: «Ваш аккаунт взломали! Перейдите по ссылке». Что делать?',
            'options': [
                'Жмакаю ссылку — вдруг правда?',
                'Пишу в поддержку через официальный сайт.',
                'Отправляю свой пароль в ответ, чтобы «проверили».'
            ],
            'correct': 1
        },
        {
            'text': 'Какой метод взлома используют чаще всего?',
            'options': [
                'Квантовый компьютер',
                'Социальная инженерия (типа «дай код из SMS»)',
                'Магические заклинания'
            ],
            'correct': 1
        },
        {
            'text': 'Что надежнее защитит твой аккаунт?',
            'options': [
                'Секретный вопрос «Девичья фамилия мамы»',
                'Двухфакторная аутентификация (2FA)',
                'Никому не говорю пароль (но записываю в Notes)'
            ],
            'correct': 1
        },
        {
            'text': 'Ты скачал «взломанную» игру. Что будет?',
            'options': [
                'Бесплатный гейминг — мечта!',
                'Мой ПК теперь майнит крипту для хакеров.',
                'Получу бан за читы.'
            ],
            'correct': 1
        },
        {
            'text': 'Как выглядит безопасное соединение в браузере?',
            'options': [
                '🔒 https:// + замок',
                'http:// + восклицательный знак',
                'Без разницы, я везде логинюсь.'
            ],
            'correct': 0
        },
        {
            'text': 'Хакеры атаковали школу. Какой пароль спасет?',
            'options': [
                'admin',
                'яНеЗнаюПароль123',
                '3R$9!xQp#Lm2'
            ],
            'correct': 2
        },
        {
            'text': 'Твой друг просит войти в его соцсеть «проверить сообщение». Пустишь?',
            'options': [
                'Да, мы же друзья!',
                'Нет, это может быть фейковый аккаунт.',
                'Только если он пришлет мне свой пароль.'
            ],
            'correct': 1
        },
        {
            'text': 'Куда хакеру проще всего ломать?',
            'options': [
                'Через суперкомпьютер NASA',
                'Через роутер с паролем «admin»',
                'Через чайник с Wi-Fi'
            ],
            'correct': 1
        },
        {
            'text': 'Какой главный секрет безопасности?',
            'options': [
                'Никому не доверять, даже себе.',
                'Обновлять Windows, пока не надоест.',
                'Выключить интернет и жить в лесу.'
            ],
            'correct': 0
        },
    ]

    for i, q in enumerate(questions_data):
        img = images[i] if i < len(images) else ""
        question = Question(quiz_id=quiz.id, text=q['text'], image_url=img, correct_option=-1)
        db.session.add(question)
        db.session.commit()
        opts = []
        for opt_text in q['options']:
            opt = Option(question_id=question.id, text=opt_text)
            db.session.add(opt)
            db.session.commit()
            opts.append(opt)
        question.correct_option = opts[q['correct']].id
        db.session.commit()
