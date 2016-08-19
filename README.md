AIOrchestra persistence
-----------------------

In order to make AIOrchestra serialization/deserialization mechanism to be more robust, it is necessary to have a persistence model.
In this repository you can find ORM models for AIOrchestra deployment context and its nodes entities.

To specify where to map ORM models, please change in `alembic.ini` next line from:

    sqlalchemy.url = sqlite:////tmp/aiorchestra.sqlite

to exact location of a database to use with AIOrchestra persistence.