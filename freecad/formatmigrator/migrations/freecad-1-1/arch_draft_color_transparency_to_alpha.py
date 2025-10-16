# SPDX-License-Identifier: LGPL-2.1-or-later

from datetime import date
from typing import Tuple

from packaging.version import Version
from xml.etree.ElementTree import Element

from freecad.formatmigrator.migrator import Migrator
from freecad.formatmigrator.xml_utilities import find_elements_by_type


class ArchDraftColorTransparencyToAlpha(Migrator):
    name = "Arch/Draft color transparency to alpha"
    description = "Convert color transparency to alpha (i.e., 1-transparency) in Arch and Draft"
    changed_in_freecad_version = Version("1.1")
    changed_on_date = date(2024, 12, 9)
    changed_in_hash = "0607c555d6c56d1b617dc0d3a52431bef562c7dc"

    """Affected elements:
    ArchBuildingPart Transparency
    ArchCurtainWall Transparency
    ArchPanel Transparency
    ArchWall Transparency
    ArchWindow Transparency
    Draft DiffuseColor"""

    def forward(self, document_xml: Element, gui_document_xml: Element):
        """Part's "color" property was an RGBT, is now RGBA: to migrate, the fourth component of a
        color entry must be converted from transparency to alpha."""
        color_elements = find_elements_by_type(gui_document_xml, "App::PropertyColor")
        for color_element in color_elements:
            r, g, b, t = self.decode_color_from_packed_value(int(color_element.text))
            a = 1.0 - t
            color_element.text = str(self.encode_color_to_packed_value((r, g, b, a)))

    def backward(self, document_xml: Element, gui_document_xml: Element):
        color_elements = find_elements_by_type(gui_document_xml, "App::PropertyColor")
        for color_element in color_elements:
            r, g, b, a = self.decode_color_from_packed_value(int(color_element.text))
            t = 1.0 - a
            color_element.text = str(self.encode_color_to_packed_value((r, g, b, t)))

    @staticmethod
    def decode_color_from_packed_value(color: int) -> Tuple[float, float, float, float]:
        """Given a color integer from a FreeCAD PropertyColor node, decode it into RGBX."""
        r = (color >> 24) / 255.0
        g = ((color >> 16) & 0xFF) / 255.0
        b = ((color >> 8) & 0xFF) / 255.0
        x = (color & 0xFF) / 255.0
        return r, g, b, x

    @staticmethod
    def encode_color_to_packed_value(color: Tuple[float, float, float, float]) -> int:
        """Given a color tuple, encode it into a FreeCAD PropertyColor integer."""
        r, g, b, x = color
        return (
            int(round(r * 255.0)) << 24
            | int(round(g * 255.0)) << 16
            | int(round(b * 255.0)) << 8
            | int(round(x * 255.0))
        )
