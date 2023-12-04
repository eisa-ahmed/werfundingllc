odoo.define('credit_application.dynamic_required_fields', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.DynamicRequiredFields = publicWidget.Widget.extend({
        selector: '.s_website_form_field',

        start: function () {
            var self = this;
            var fieldsToMonitor = [
                'contact_name_last2', 'birth_date2', 'mobile2', 'email2',
                'social_security_no2', 'city2', 'zip2', 'business_owner_street2',
                'ownership_percent2', 'credit_score_estimate2', 'sign_2', 'title_2', 'date_2'
            ];


            fieldsToMonitor.forEach(function(fieldName) {
                self.$('.s_website_form_input[name="' + fieldName + '"]').on('input', function() {
                    self._updateRequiredFields(fieldsToMonitor);
                });
            });
        },

        _updateRequiredFields: function (fieldsToMonitor) {
            var self = this;
            var fieldsFilled = fieldsToMonitor.some(function(fieldName) {
                var field = self.$('.s_website_form_input[name="' + fieldName + '"]');
                return field.length > 0 && field.val().trim() !== '';
            });

            var contactName2Field = $('input[name="contact_name2"]'); // Search globally on the page
            contactName2Field.prop('required', fieldsFilled);
        },
    });
});
