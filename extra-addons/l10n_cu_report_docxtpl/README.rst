.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========
Report Docxtpl
===========

The docxtpl reporting engine is a reporting engine for Odoo based on `Libreoffice <http://www.libreoffice.org/>`_:

* the report is created in DOCX,
* the report is stored on the server in docx format
* the report is sent to the user in any output format supported by Libreoffice (ODT, PDF, HTML, DOC, DOCX, Docbook, XLS, etc.)

The key advantages of a Libreoffice based reporting engine are:

* no need to be a developer to create or modify a report: the report is created and modified with Libreoffice. So this reporting engine has a full WYSIWYG report development tool!
* For a PDF report in A4/Letter format, it's easier to develop it with a tool such as Libreoffice that is designed to create A4/Letter documents than to develop it in HTML/CSS, also some print peculiarities (backgrounds, margin boxes) are not very well supported by the HTML/CSS based solutions.
* If you want your users to be able to modify the document after its generation by Odoo, just configure the document with DOCX output (or DOC or ODT) and the user will be able to modify the document with Libreoffice (or Word) after its generation by Odoo.

Installation
============

Install the required python libs:

.. code::

  pip install docx
  pip install docxtpl

To allow the conversion of docx reports to other formats (PDF, ODT, DOC, etc.), install libreoffice:

.. code::

  apt-get --no-install-recommends install libreoffice

Configuration
=============

For example, to replace the native invoice report by a custom docxtpl report, add the following XML file in your custom module:

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="account.account_invoices" model="ir.actions.report.xml">
      <field name="report_type">docxtpl</field>
      <field name="docxtpl_filetype">docx</field>
      <field name="module">my_custom_module_base</field>
      <field name="docxtpl_template_fallback">report/account_invoice.docx</field>
  </record>

  </odoo>

where *my_custom_module_base* is the name of the custom Odoo module. In this example, the invoice DOCX file is located in *my_custom_module_base/report/account_invoice.docx*.

It's also possible to reference a template located in a trusted path of your
Odoo server. In this case you must let the *module* entry empty and specify
the path to the template as *docxtpl_template_fallback*.

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="account.account_invoices" model="ir.actions.report.xml">
      <field name="report_type">docxtpl</field>
      <field name="docxtpl_filetype">docx</field>
      <field name="docxtpl_template_fallback">/odoo/templates/docxtpl/report/account_invoice.docx</field>
  </record>

  </odoo>

Moreover, you must also modify the Odoo server configuration file to declare
the allowed root directory for your docxtpl templates. Only templates located
into this directory can be loaded by docxtpl report.

.. code::

  [options]
  ...

  [l10n_cu_report_docxtpl]
  root_tmpl_path=/odoo/templates/docxtpl

If you want an invoice in PDF format instead of ODT format, the XML file should look like:

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="account.account_invoices" model="ir.actions.report.xml">
      <field name="report_type">docxtpl</field>
      <field name="docxtpl_filetype">pdf</field>
      <field name="module">my_custom_module_base</field>
      <field name="docxtpl_template_fallback">report/account_invoice.docx</field>
  </record>

  </odoo>

If you want to add a new docxtpl PDF report (and not replace a native report), the XML file should look like this:

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="partner_summary_report" model="ir.actions.report.xml">
      <field name="name">Partner Summary</field>
      <field name="model">res.partner</field>
      <field name="report_name">res.partner.summary</field>
      <field name="report_type">docxtpl</field>
      <field name="docxtpl_filetype">pdf</field>
      <field name="module">my_custom_module_base</field>
      <field name="docxtpl_template_fallback">report/partner_summary.docx</field>
  </record>

  <!-- Add entry in "Print" drop-down list -->
  <record id="button_partner_summary_report" model="ir.values">
      <field name="key2">client_print_multi</field>
      <field name="model">res.partner</field>
      <field name="name">Partner Summary</field>
      <field name="value" eval="'ir.actions.report.xml,%d'%partner_summary_report" />
  </record>

  </odoo>

Configuration parameters
------------------------

docxtpl.conversion_command
    The command to be used to run the conversion, ``libreoffice`` by default. If you change this, whatever you set here must accept the parameters ``--headless --convert-to $ext $file`` and put the resulting file into ``$file``'s directory with extension ``$ext``. The command will be started in ``$file``'s directory.

Usage
=====
The templating language is `extensively documented <https://docxtpl.readthedocs.io/en/latest/>`_, the records are exposed in libreoffice as ``objects``, on which you can also call functions.

Available functions and objects
-------------------------------

user
    Browse record of current user
lang
    The user's company's language as string (ISO code)
b64decode
    ``base64.b64decode``
html_sanitize(string)
    Sanitize HTML string
time
    Python's ``time`` module
display_address(partner)
    Return a formatted string of the partner's address

Credits
=======
* This module is based on the `OCA <https://odoo-community.org>`_ reporting engine `report_py3o <https://github.com/OCA/reporting-engine/tree/10.0/report_py3o>`_

