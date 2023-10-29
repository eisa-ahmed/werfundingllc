# -*- coding: utf-8 -*- 
import getpass

import psycopg2 as pg
from odoo import models, fields
from odoo.exceptions import ValidationError

class DataCorrect(models.Model):
    _name = 'data.correct'
    _description = 'Data Correct'

    python_code = fields.Text(string="Python Code")
    field_querry = fields.Text(string="SQL Querry")
    result = fields.Char(string="Result")
    purpose = fields.Char(string="purpose")

    def run_python_code(self):
        try:
            exec(self.python_code)
        except Exception as e:
            raise ValidationError('Error..!\n' + str(e))

    def run_sql_querry(self):

        user_name = getpass.getuser()
        database_name = self._cr.dbname
        conn = pg.connect(database=database_name, user=user_name)
        cur = conn.cursor()
        cur.execute(self.field_querry)
        rows_deleted = cur.rowcount
        conn.commit()
