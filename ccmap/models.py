from . import db

class ChildcareCenter(db.Model):
    __tablename__ = "childcare_map"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.Integer)
    owner = db.Column(db.String(100))
    address = db.Column(db.String(100))
    url = db.Column(db.String(255))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    info = db.Column(db.Text)
    location_last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return (f'ChildcareCenter(id={self.id!r},'
                f'name={self.name!r},'
                f'address={self.address!r},'
                f'phone_number={self.phone_number!r},'
                f'owner={self.owner!r},'
                f'url={self.url!r},'
                f'lat={self.lat!r},'
                f'lng={self.lng!r},'
                f'location_last_updated={self.location_last_updated!r}'
                )
