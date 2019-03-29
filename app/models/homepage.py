from app import db


class HomePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(64))
    subhead = db.Column(db.Text)
    about = db.Column(db.Text)
    statement = db.Column(db.Text)

    def update(self, **kwargs):
        self.caption = kwargs.get('caption', self.caption)
        self.subhead = kwargs.get('subhead', self.subhead)
        self.about = kwargs.get('about', self.about)
        self.statement = kwargs.get('statement', self.statement)
        db.session.add(self)
        db.session.commit()
