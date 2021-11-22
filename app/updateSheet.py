#!/usr/bin/env python
# coding: utf-8

from sqlalchemy.orm import Query
import json

from sheetsParser import Spreadsheet


def text_cells(spreadsheet: Spreadsheet, texts: Query):
    cells_range = f'A:F'
    spreadsheet.prepare_set_values(
        cells_range=cells_range,
        values=[['text_id'] + [text.text_id for text in texts],
                ['step'] + [text.step for text in texts],
                ['title'] + [text.title for text in texts],
                ['text'] + [text.text for text in texts],
                ['attachment'] + [text.attachment for text in texts],
                ['date'] + [text.date.strftime("%d/%m/%Y %H:%M:%S") if text.date else None for text in texts]],
        major_dimension='COLUMNS')

    spreadsheet.prepare_set_cells_format('A:F', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE'})
    spreadsheet.prepare_set_cells_format('D:D', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'LEFT',
                                                 'verticalAlignment': 'MIDDLE'})
    spreadsheet.prepare_set_columns_width(0, 1, 50)
    spreadsheet.prepare_set_columns_width(2, 6, 150)
    spreadsheet.prepare_set_column_width(3, 380)
    spreadsheet.prepare_set_cells_format('F:F', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE',
                                                 'numberFormat': {'type': 'DATE_TIME',
                                                                  'pattern': ''}})

    spreadsheet.run_prepared()


def user_cells(spreadsheet: Spreadsheet, users):
    cells_range = f'A:I'
    spreadsheet.prepare_set_values(
        cells_range=cells_range,
        values=[['chat_id'] + [user.chat_id for user in users],
                ['domain'] + [user.domain for user in users],
                ['first_name'] + [user.first_name for user in users],
                ['last_name'] + [user.last_name for user in users],
                ['step'] + [user.step for user in users],
                ['texts'] + [user.texts for user in users],
                ['admin'] + [user.admin for user in users],
                ['lectures'] + [user.lectures for user in users],
                ['date'] + [user.date.strftime("%d/%m/%Y %H:%M:%S") if user.date else None for user in users]],
        major_dimension='COLUMNS')

    spreadsheet.prepare_set_cells_format('A:I', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE'})
    spreadsheet.prepare_set_columns_width(0, 6, 100)
    spreadsheet.prepare_set_column_width(7, 380)
    spreadsheet.prepare_set_column_width(8, 150)
    spreadsheet.prepare_set_cells_format('I:I', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE',
                                                 'numberFormat': {'type': 'DATE_TIME',
                                                                  'pattern': ''}})

    spreadsheet.run_prepared()


def step_cells(spreadsheet: Spreadsheet, steps):
    cells_range = f'A:C'
    spreadsheet.prepare_set_values(
        cells_range=cells_range,
        values=[['number'] + [step.number for step in steps],
                ['name'] + [step.name for step in steps],
                ['date'] + [step.date.strftime("%d/%m/%Y %H:%M:%S") if step.date else None for step in steps]],
        major_dimension='COLUMNS')

    spreadsheet.prepare_set_cells_format('A:C', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE'})
    spreadsheet.prepare_set_column_width(0, 100)
    spreadsheet.prepare_set_column_width(1, 350)
    spreadsheet.prepare_set_column_width(2, 150)
    spreadsheet.prepare_set_cells_format('C:C', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE',
                                                 'numberFormat': {'type': 'DATE_TIME',
                                                                  'pattern': ''}})

    spreadsheet.run_prepared()


def attachment_cells(spreadsheet: Spreadsheet, attachments):
    cells_range = f'A:A'
    spreadsheet.prepare_set_values(
        cells_range=cells_range,
        values=[['name'] + [attachment.name for attachment in attachments]],
        major_dimension='COLUMNS')

    spreadsheet.prepare_set_cells_format('A:A', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE'})
    spreadsheet.prepare_set_column_width(0, 400)

    spreadsheet.run_prepared()


def command_sells(spreadsheet: Spreadsheet, commands):
    cells_range = f'A:C'
    spreadsheet.prepare_set_values(
        cells_range=cells_range,
        values=[['name'] + [command.name for command in commands],
                ['arguments'] + [';\n'.join(json.loads(command.arguments)) for command in commands],
                ['admin'] + [command.admin for command in commands]],
        major_dimension='COLUMNS')

    spreadsheet.prepare_set_cells_format('A:C', {'wrapStrategy': 'WRAP',
                                                 'horizontalAlignment': 'CENTER',
                                                 'verticalAlignment': 'MIDDLE'})
    spreadsheet.prepare_set_column_width(0, 150)
    spreadsheet.prepare_set_column_width(1, 200)
    spreadsheet.prepare_set_column_width(2, 100)

    spreadsheet.run_prepared()
