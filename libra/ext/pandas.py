"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains the `PandasMixin` object, which extends pandas DataFrame conversion 
to ORM table instances.
"""

# ==============================================================================

from typing import (
    Iterable, 
    Self
)

import sqlalchemy
import pandas as pd

# ==============================================================================

class PandasMixin:
    """
    Mixin object to add support for the Pandas Data Analysis Library, 
    specifically the conversion to/from Pandas Series objects and DataFrame 
    objects. Inject into a class first inheriting from LibraMetaClass. 
    """

    def to_series(self) -> pd.Series:
        """Convert instance to Pandas Series object"""

        return pd.Series(self.to_dict())
    
    @classmethod
    def to_frame(cls, instances : Iterable[Self]) -> pd.DataFrame:
        """Convert list of instances to a Pandas DataFrame object"""

        return pd.DataFrame([instance.to_dict() for instance in instances])
    
    @classmethod
    def from_series(cls, series : pd.Series) -> Self:
        values = []

        for col in cls.__table__.columns:
            val = series.get(col.name)

            if pd.isna(val):
                values.append(None)
                continue

            python_type = col.type.python_type
            if isinstance(col.type, (sqlalchemy.DateTime, sqlalchemy.Date, sqlalchemy.Time)):
                val = pd.to_datetime(val).to_pydatetime()
            else:
                val = python_type(val)
            
            values.append(val)
        
        return cls(*values)

    @classmethod
    def from_frame(cls, df : pd.DataFrame) -> list[Self]:
        records = df.to_dict(orient = 'records')
        instances = []

        for record in records:
            values = []
            for col in cls.__table__.columns:
                val = record.get(col.name)

                if pd.isna(val):
                    values.append(None)
                    continue

                python_type = col.type.python_type
                if isinstance(col.type, (sqlalchemy.DateTime, sqlalchemy.Date, sqlalchemy.Time)):
                    val = pd.to_datetime(val).to_pydatetime()
                else:
                    val = python_type(val)

                values.append(val)
                
            instances.append(cls(*values))
        
        return instances
