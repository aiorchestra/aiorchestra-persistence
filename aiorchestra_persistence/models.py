#    Author: Denys Makogon
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sqlalchemy as sa

from sqlalchemy import exc
from sqlalchemy import orm
from sqlalchemy.ext import declarative

Base = declarative.declarative_base()


def with_session(action):
    def wrapper(*args, **kwargs):
        self_or_class = list(args)[1]
        if not hasattr(self_or_class, 'engine'):
            raise Exception("Engine for ORM model was not configured.")
        try:
            session = orm.sessionmaker(bind=self_or_class.engine)
            setattr(self_or_class, 'session', session)
            action(*args, **kwargs)
        except (exc.SQLAlchemyError, Exception):
            if hasattr(self_or_class, 'session'):
                del self_or_class.session
    return wrapper


class BaseDatabaseModel(object):

    @with_session
    def save(self, engine):
        self.session.add(self)
        self.session.commit()

    @with_session
    def delete(self, engine):
        self.session.delete(self)
        self.session.commit()

    @with_session
    def update(self, engine, **values):
        try:
            for key in values:
                if hasattr(self, key):
                    setattr(self, key, values[key])
            self.save(engine)
            return self.find_by(engine, name=self.name)
        except Exception as e:
            raise e

    @classmethod
    def list(cls, engine):
        return cls.session.query(cls).all()

    @classmethod
    def find_by(cls, engine, **kwargs):
        obj = cls.session.query(cls).filter_by(**kwargs).first()
        return obj if obj else None

    @classmethod
    def get_all_by(cls, engine, **kwargs):
        objs = cls.session.query(cls).filter_by(**kwargs).all()
        return objs if objs else []


class ContextModel(Base, BaseDatabaseModel):
    __tablename__ = "context"

    name = sa.Column(sa.String(), primary_key=True,
                     nullable=False, unique=True)
    status = sa.Column(sa.String(), nullable=False)
    template_path = sa.Column(sa.String(), nullable=False)
    inputs = sa.Column(sa.Text(), nullable=False)

    def __init__(self, context, engine):
        s_context = context.serialize()

        self.name = s_context['name']
        self.status = s_context['status']
        self.template_path = s_context['template_path']
        self.inputs = s_context['inputs']
        self.save()
        for node in s_context['nodes']:
            ContextNodeModel(engine, context, node)

    def jsonify(self):
        return {
            'name': self.name,
            'status': self.status,
            'template_path': self.template_path,
            'inputs': self.inputs,
        }

    @classmethod
    def assemble(cls, name, engine):
        new_context = cls.find_by(engine, name=name).jsonify()
        nodes = [node.jsonify() for node in
                 ContextNodeModel.get_all_by(
                     engine, context=new_context.name)]
        new_context.update(nodes=nodes,
                           path=new_context['template_path'])


class ContextNodeModel(Base, BaseDatabaseModel):
    __tablename__ = "node"

    context = sa.Column(sa.ForeignKey('context.name'))
    name = sa.Column(sa.String(), nullable=False, unique=True)
    is_provisioned = sa.Column(sa.Boolean(), nullable=False)
    properties = sa.Column(sa.Text(), nullable=True)
    attributes = sa.Column(sa.Text(), nullable=True)
    runtime_properties = sa.Column(sa.Text(), nullable=True)

    def __init__(self, engine, context, node):
        self.context = context.name
        self.name = node['__name']
        self.is_provisioned = node['is_provisioned']
        self.properties = node['__properties']
        self.attributes = node['__attributes']
        self.runtime_properties = node['runtime_properties']

        self.save(engine)

    def jsonify(self):
        return {
            'name': self.name,
            'is_provisioned': self.is_provisioned,
            '__properties': self.properties,
            '__attributes': self.attributes,
            'runtime_properties': self.runtime_properties,
        }
