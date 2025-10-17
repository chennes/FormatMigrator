# SPDX-License-Identifier: LGPL-2.1-or-later

from datetime import date

from packaging.version import Version
from xml.etree.ElementTree import Element

from freecad.formatmigrator.migrator import Migrator


class AttachmentExtensionSupportToAttachmentSupport(Migrator):
    name = "AttachmentExtension::Support to AttachmentSupport"
    description = "Rename the AttachExtension::Support element to AttachmentSupport"
    changed_in_freecad_version = Version("1.0")
    changed_on_date = date(2024, 3, 4)
    changed_in_hash = "a8ae56e06ab0c45205f1f185523c23fe99d5ce44"

    def forward(self, document_xml: Element, gui_document_xml: Element):
        Migrator.rename_property(document_xml, "Support", "AttachmentSupport")

    def backward(self, document_xml: Element, gui_document_xml: Element):
        Migrator.rename_property(document_xml, "AttachmentSupport", "Support")
