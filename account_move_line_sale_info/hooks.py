# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ast

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):

    """ INIT sale references in acount move line """
    # FOR stock moves
    cr.execute(
        """
        update account_move_line aml set sale_line_id = sm.sale_line_id
        FROM account_move_line aml2
        INNER JOIN stock_move sm ON
        aml2.stock_move_id = sm.id
        WHERE aml.id = aml2.id;
    """
    )
    # FOR invoices
    cr.execute(
        """
        update account_move_line aml set sale_line_id = sol.id
        FROM account_move_line aml2
        INNER JOIN account_invoice ai ON
        ai.id = aml2.invoice_id
        INNER JOIN account_invoice_line ail ON
        ail.invoice_id = ai.id
        INNER JOIN sale_order_line_invoice_rel rel ON
        rel.invoice_line_id = ail.id
        INNER JOIN sale_order_line sol ON
        rel.order_line_id = sol.id
        AND sol.product_id = aml2.product_id
        WHERE aml.id = aml2.id;
    """
    )

    # NOW we can fill the SO
    cr.execute(
        """
        UPDATE account_move_line aml
        SET sale_id = sol.order_id
        FROM sale_order_line AS sol
        WHERE aml.sale_line_id = sol.id
        RETURNING aml.move_id
    """
    )

    # NOW we can fill the lines without invoice_id (Odoo put it very
    # complicated)

    cr.execute(
        """
        UPDATE account_move_line aml
        SET sale_id = so.id
        FROM sale_order_line so
        LEFT JOIN account_move_line aml2
        ON aml2.sale_id = so.id
        WHERE aml2.move_id = aml.move_id
    """
    )

    cr.execute(
        """
        update account_move_line aml set sale_line_id = sol.id
        FROM account_move_line aml2
        INNER JOIN sale_order so ON
        so.id = aml2.sale_id
        INNER JOIN sale_order_line sol ON
        so.id = sol.order_id
        AND sol.product_id = aml2.product_id
        WHERE aml.id = aml2.id;
    """
    )
