from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
page_size = 10
categories = db.Table(
    'categories',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
    db.Column('video_id', db.Integer, db.ForeignKey('video.id')),
    db.UniqueConstraint('category_id', 'video_id', name='uix_1')
)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(500))
    categories = db.relationship('Category', secondary=categories, backref=db.backref('videos', lazy='dynamic'))

    __mapper_args__ = {
        "order_by": title
    }

    def __init__(self, title, description=''):
        self.title = title
        self.description = description

    def __repr__(self):
        return '<Video %r>' % self.title

    def get_videos_by_categories(self):
        return self.query.filter(
            Video.categories.any(Category.id.in_([o.id for o in self.categories])),
            Video.id != self.id).join(Video.categories).group_by('category_id', 'video_id').distinct('video_id')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    __mapper_args__ = {
        "order_by": name
    }

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


@app.route('/')
def video_list():
    return render_template('video_list.html', videos=Video.query.all())


@app.route('/video/<int:video_id>')
def video_detail(video_id):
    video = Video.query.get(video_id)
    videos = video.get_videos_by_categories()
    return render_template('video_detail.html', page_size=page_size, video=video, videos=videos.limit(page_size),
                           total_videos=len(videos.all()))


@app.route('/videos/<int:video_id>/<int:page>')
def load_videos(video_id, page):
    video = Video.query.get(video_id)
    videos = video.get_videos_by_categories()
    return render_template('video_list.html', video=video, videos=videos.limit(page_size).offset(page_size * page),
                           page_size=page_size, page=page + 1, total_pages=videos.count() / page_size)


if __name__ == '__main__':
    app.run()
