from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

@classmethod
def get_or_create(model, session, **kwargs):
  instance = session.query(model).filter_by(**kwargs).first()
  if instance:
    return instance
  else:
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance

Base.get_or_create = get_or_create