/** @odoo-module **/

import { NewContentModal, MODULE_STATUS } from '@website/systray_items/new_content';
import { patch } from 'web.utils';
import Dialog from 'web.Dialog';
import { qweb, _t } from 'web.core';
const ajax = require('web.ajax');

patch(NewContentModal.prototype, 'website_blog_new_content_lms', {
    setup() {
        this._super();

        const newBlogElement = this.state.newContentElements.find(element => element.moduleXmlId === 'base.module_website_blog');
        newBlogElement.createNewContent = () => this.newlmscourse();
        newBlogElement.status = MODULE_STATUS.INSTALLED;
    },

    async newlmscourse() {
        var ChannelCreateDialog = Dialog.extend({
            template: 'website.lms.course.create',
            xmlDependencies: Dialog.prototype.xmlDependencies.concat(
                ['/openeducat_lms_website/static/src/xml/website_lms_course.xml']
            ),
            /**
             * @override
             * @param {Object} parent
             * @param {Object} options
             */
            init: function (parent, options) {
                options = _.defaults(options || {}, {
                    title: _t("New Course"),
                    size: 'medium',
                    buttons: [{
                        text: _t("Create"),
                        classes: 'btn-primary',
                        click: this._onClickFormSubmit.bind(this)
                    }, {
                        text: _t("Discard"),
                        close: true
                    },]
                });
                this._super(parent, options);
            },
            start: function () {
                var self = this;
                return this._super.apply(this, arguments).then(function () {
                    var $input = self.$('#category_ids');
                    $input.select2({
                        width: '100%',
                        allowClear: true,
                        formatNoMatches: false,
                        multiple: true,
                        selection_data: false,
                        fill_data: function (query, data) {
                            var that = this,
                                tags = { results: [] };
                            _.each(data, function (obj) {
                                if (that.matcher(query.term, obj.name)) {
                                    tags.results.push({ id: obj.id, text: obj.name });
                                }
                            });
                            query.callback(tags);
                        },
                        query: function (query) {
                            var that = this;
                            // fetch data only once and store it
                            if (!this.selection_data) {
                                ajax.jsonRpc('/lms/category/search_read', 'call', {
                                    fields: ['name'],
                                    domain: [],
                                }).then(function (data) {
                                    that.can_create = data.can_create;
                                    that.fill_data(query, data.read_results);
                                    that.selection_data = data.read_results;
                                });
                            } else {
                                this.fill_data(query, this.selection_data);
                            }
                        }
                    });
                });
            },
            _onClickFormSubmit: function (ev) {
                var $form = this.$("#lms_course_add_form");
                var $title = this.$("#title");
                if (!$title[0].value) {
                    $title.addClass('border-danger');
                    this.$("#title-required").removeClass('d-none');
                } else {
                    $form.submit();
                }
            },
        });
        var dialog = new ChannelCreateDialog(self, {});
        dialog.open();
    }
});
