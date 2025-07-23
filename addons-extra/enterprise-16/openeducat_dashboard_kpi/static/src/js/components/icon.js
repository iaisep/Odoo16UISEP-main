/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { onWillStart, useRef, useState } = owl;

export class Icon extends CharField {

    setup() {
        super.setup();
        this.iconModal = useRef("iconModal");
        this.searchInput = useRef("searchInput");
        this.state = useState({
            searchedIcon: false
        });
        onWillStart(() => {
            this.icon_set = ['home', 'check','times', 'clock-o', 'question', 'car', 'calendar', 'calendar-times-o', 'bar-chart', 'commenting-o', 'star-half-o', 'address-book-o', 'tachometer', 'search', 'money', 'line-chart', 'area-chart', 'pie-chart', 'check-square-o', 'users', 'shopping-cart', 'truck', 'user-circle-o', 'user-plus', 'sun-o', 'paper-plane', 'rss', 'gears', 'book'];
        });
    }

    onClickIconSelector() {
        $(this.iconModal.el).modal('show');
    }

    onIconClick(e) {
        this.props.update(e.target.dataset.icon);
        $(this.iconModal.el).modal('hide');
    }

    onSearch() {
        this.state.searchedIcon = this.searchInput.el.value;
    }

    onInput(e) {
        if (e.keyCode == 13) {
            this.onSearch()
        }
    }

    onClear() {
        this.props.update('');
    }
}

Icon.template = 'DashboardFieldBinaryImage';

registry.category("fields").add("image_widget_pro", Icon);
