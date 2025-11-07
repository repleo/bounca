from unittest.mock import Mock, patch

from django.test import TestCase
from crispy_forms.utils import TEMPLATE_PACK

from vuetifyforms.components import (
    VueFlex, VueSpacer, VueImports, VueMethods, VueField, VueScriptElem
)


class VueFlexTest(TestCase):
    """Unit tests voor VueFlex"""

    def test_template_attribute(self):
        """Test dat VueFlex de juiste template heeft"""
        flex = VueFlex('field1', 'field2')
        self.assertEqual(flex.template, "%s/layout/flex.html")

    def test_initialization_with_fields(self):
        """Test VueFlex initialisatie met velden"""
        flex = VueFlex('field1', 'field2', 'field3')
        self.assertIsNotNone(flex)

    def test_inherits_from_div(self):
        """Test dat VueFlex van Div overerft"""
        from crispy_forms.layout import Div
        flex = VueFlex('field1')
        self.assertIsInstance(flex, Div)


class VueSpacerTest(TestCase):
    """Unit tests voor VueSpacer"""

    def test_template_attribute(self):
        """Test dat VueSpacer de juiste template heeft"""
        spacer = VueSpacer()
        self.assertEqual(spacer.template, "%s/layout/spacer.html")

    def test_inherits_from_div(self):
        """Test dat VueSpacer van Div overerft"""
        from crispy_forms.layout import Div
        spacer = VueSpacer()
        self.assertIsInstance(spacer, Div)


class VueScriptElemTest(TestCase):
    """Unit tests voor VueScriptElem (abstract base class)"""

    def test_initialization_with_elems(self):
        """Test VueScriptElem initialisatie met elementen"""

        class TestScriptElem(VueScriptElem):
            template = "%s/script/test.js"

        elem = TestScriptElem(['elem1', 'elem2'])
        self.assertEqual(elem.elems, ['elem1', 'elem2'])

    def test_initialization_with_custom_template(self):
        """Test VueScriptElem met custom template"""

        class TestScriptElem(VueScriptElem):
            template = "%s/script/default.js"

        elem = TestScriptElem(['elem1'], template="%s/script/custom.js")
        self.assertEqual(elem.template, "%s/script/custom.js")

    @patch('vuetifyforms.components.render_to_string')
    def test_render_calls_render_to_string(self, mock_render):
        """Test dat render render_to_string aanroept"""

        class TestScriptElem(VueScriptElem):
            template = "%s/script/test.js"

        mock_render.return_value = "rendered content"
        elem = TestScriptElem(['elem1'])

        form = Mock()
        form_style = Mock()
        context = {}

        result = elem.render(form, form_style, context)

        mock_render.assert_called_once()
        self.assertEqual(result, "rendered content")

    @patch('vuetifyforms.components.render_to_string')
    def test_render_with_template_pack(self, mock_render):
        """Test render met custom template pack"""

        class TestScriptElem(VueScriptElem):
            template = "%s/script/test.js"

        mock_render.return_value = "content"
        elem = TestScriptElem(['elem1'])

        elem.render(Mock(), Mock(), {}, template_pack='custom_pack')

        mock_render.assert_called_once()

    @patch('vuetifyforms.components.render_to_string')
    def test_render_passes_script_in_context(self, mock_render):
        """Test dat render script in context doorgeeft"""

        class TestScriptElem(VueScriptElem):
            template = "%s/script/test.js"

        elem = TestScriptElem(['elem1'])
        elem.render(Mock(), Mock(), {})

        call_args = mock_render.call_args
        context_passed = call_args[0][1]
        self.assertIn('script', context_passed)
        self.assertEqual(context_passed['script'], elem)


class VueImportsTest(TestCase):
    """Unit tests voor VueImports"""

    def test_template_attribute(self):
        """Test dat VueImports de juiste template heeft"""
        imports = VueImports(['import1', 'import2'])
        self.assertEqual(imports.template, "%s/script/imports.js")

    def test_inherits_from_vue_script_elem(self):
        """Test dat VueImports van VueScriptElem overerft"""
        imports = VueImports(['import1'])
        self.assertIsInstance(imports, VueScriptElem)

    def test_initialization_stores_elems(self):
        """Test dat elementen correct worden opgeslagen"""
        imports = VueImports(['import1', 'import2', 'import3'])
        self.assertEqual(imports.elems, ['import1', 'import2', 'import3'])


class VueMethodsTest(TestCase):
    """Unit tests voor VueMethods"""

    def test_template_attribute(self):
        """Test dat VueMethods de juiste template heeft"""
        methods = VueMethods(['method1', 'method2'])
        self.assertEqual(methods.template, "%s/script/methods.js")

    def test_inherits_from_vue_script_elem(self):
        """Test dat VueMethods van VueScriptElem overerft"""
        methods = VueMethods(['method1'])
        self.assertIsInstance(methods, VueScriptElem)

    def test_initialization_stores_elems(self):
        """Test dat elementen correct worden opgeslagen"""
        methods = VueMethods(['method1', 'method2'])
        self.assertEqual(methods.elems, ['method1', 'method2'])


class VueFieldTest(TestCase):
    """Unit tests voor VueField"""

    def test_template_attribute(self):
        """Test dat VueField de juiste template heeft"""
        field = VueField('field_name')
        self.assertEqual(field.template, "%s/field.html")

    def test_initialization_with_single_field(self):
        """Test VueField initialisatie met één veld"""
        field = VueField('field_name')
        self.assertEqual(field.fields, ['field_name'])

    def test_initialization_with_multiple_fields(self):
        """Test VueField initialisatie met meerdere velden"""
        field = VueField('field1', 'field2', 'field3')
        self.assertEqual(field.fields, ['field1', 'field2', 'field3'])

    def test_initialization_creates_empty_attrs_dict(self):
        """Test dat attrs dict wordt aangemaakt als deze niet bestaat"""
        field = VueField('field_name')
        self.assertIsInstance(field.attrs, dict)

    def test_initialization_with_css_class_new(self):
        """Test css_class toevoegen als class attribuut niet bestaat"""
        field = VueField('field_name', css_class='my-class')
        self.assertEqual(field.attrs['class'], 'my-class')

    def test_initialization_with_css_class_existing(self):
        """Test css_class toevoegen aan bestaand class attribuut"""
        field = VueField('field_name', css_class='additional-class')
        field.attrs['class'] = 'existing-class'

        # Create nieuwe instantie met existing class
        class TestField(VueField):
            attrs = {'class': 'existing-class'}

        field = TestField('field_name', css_class='additional-class')
        self.assertIn('additional-class', field.attrs['class'])

    def test_initialization_with_wrapper_class(self):
        """Test wrapper_class parameter"""
        field = VueField('field_name', wrapper_class='wrapper')
        self.assertEqual(field.wrapper_class, 'wrapper')

    def test_initialization_without_wrapper_class(self):
        """Test zonder wrapper_class parameter"""
        field = VueField('field_name')
        self.assertIsNone(field.wrapper_class)

    def test_initialization_with_custom_template(self):
        """Test custom template parameter"""
        field = VueField('field_name', template='%s/custom_field.html')
        self.assertEqual(field.template, '%s/custom_field.html')

    def test_initialization_converts_underscores_in_kwargs(self):
        """Test dat underscores worden omgezet naar dashes in attributes"""
        field = VueField('field_name', data_id='test123', aria_label='My Label')
        self.assertEqual(field.attrs['data-id'], 'test123')
        self.assertEqual(field.attrs['aria-label'], 'My Label')

    def test_initialization_with_style_attribute(self):
        """Test style attribuut"""
        field = VueField('field_name', style='color: red;')
        self.assertEqual(field.attrs['style'], 'color: red;')

    def test_initialization_with_id_attribute(self):
        """Test id attribuut"""
        field = VueField('field_name', id='custom_id')
        self.assertEqual(field.attrs['id'], 'custom_id')

    def test_initialization_preserves_existing_attrs(self):
        """Test dat bestaande attrs niet worden overschreven"""

        class TestField(VueField):
            attrs = {'existing': 'value'}

        field = TestField('field_name', new_attr='new_value')
        self.assertEqual(field.attrs['existing'], 'value')
        self.assertEqual(field.attrs['new-attr'], 'new_value')

    def test_initialization_with_multiple_data_attributes(self):
        """Test meerdere data-* attributes"""
        field = VueField(
            'field_name',
            data_value='123',
            data_type='string',
            data_enabled='true'
        )
        self.assertEqual(field.attrs['data-value'], '123')
        self.assertEqual(field.attrs['data-type'], 'string')
        self.assertEqual(field.attrs['data-enabled'], 'true')

    def test_inherits_from_field(self):
        """Test dat VueField van Field overerft"""
        from crispy_forms.layout import Field
        field = VueField('field_name')
        self.assertIsInstance(field, Field)

    def test_attrs_isolation_between_instances(self):
        """Test dat attrs geïsoleerd zijn tussen instanties"""
        field1 = VueField('field1', css_class='class1')
        field2 = VueField('field2', css_class='class2')

        self.assertNotEqual(field1.attrs, field2.attrs)
        self.assertEqual(field1.attrs['class'], 'class1')
        self.assertEqual(field2.attrs['class'], 'class2')

