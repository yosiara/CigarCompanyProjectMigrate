odoo.define('l10n_cu_calendar.CalendarView', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var form_common = require('web.form_common');
    var time = require('web.time');
    var CalendarView = require('web_calendar.CalendarView');
    var data = require('web.data');
    var _t = core._t;
    var _lt = core._lt;

    CalendarView.include({

        /**
         * Transform OpenERP event object to fullcalendar event object
         */
        event_data_transform: function (evt) {
            var self = this;
            var date_start;
            var date_stop;
            var date_delay = evt[this.date_delay] || 1.0,
                all_day = this.all_day ? evt[this.all_day] : false,
                res_computed_text = '',
                the_title = '',
                attendees = [];

            if (!all_day) {
                date_start = time.auto_str_to_date(evt[this.date_start]);
                date_stop = this.date_stop ? time.auto_str_to_date(evt[this.date_stop]) : null;
            } else {
                date_start = time.auto_str_to_date(evt[this.date_start].split(' ')[0], 'start');
                date_stop = this.date_stop ? time.auto_str_to_date(evt[this.date_stop].split(' ')[0], 'start') : null;
            }

            if (this.info_fields) {
                var temp_ret = {};
                res_computed_text = this.how_display_event;

                _.each(this.info_fields, function (fieldname) {
                    var value = evt[fieldname];
                    if (_.contains(["many2one"], self.fields[fieldname].type)) {
                        if (value === false) {
                            temp_ret[fieldname] = null;
                        } else if (value instanceof Array) {
                            temp_ret[fieldname] = value[1]; // no name_get to make
                        } else if (_.contains(["date", "datetime"], self.fields[fieldname].type)) {
                            temp_ret[fieldname] = formats.format_value(value, self.fields[fieldname]);
                        } else {
                            throw new Error("Incomplete data received from dataset for record " + evt.id);
                        }
                    } else if (_.contains(["one2many", "many2many"], self.fields[fieldname].type)) {
                        if (value === false) {
                            temp_ret[fieldname] = null;
                        } else if (value instanceof Array) {
                            temp_ret[fieldname] = value; // if x2many, keep all id !
                        } else {
                            throw new Error("Incomplete data received from dataset for record " + evt.id);
                        }
                    } else {
                        temp_ret[fieldname] = value;
                    }
                    res_computed_text = res_computed_text.replace("[" + fieldname + "]", temp_ret[fieldname]);
                });


                if (res_computed_text.length) {
                    the_title = res_computed_text;
                } else {
                    var res_text = [];
                    _.each(temp_ret, function (val, key) {
                        if (typeof (val) === 'boolean' && val === false) {
                        } else {
                            res_text.push(val);
                        }
                    });
                    the_title = res_text.join(', ');
                }
                the_title = _.escape(the_title);


                var the_title_avatar = '';

                if (!_.isUndefined(this.attendee_people)) {
                    var MAX_ATTENDEES = 3;
                    var attendee_showed = 0;
                    var attendee_other = '';

                    _.each(temp_ret[this.attendee_people],
                        function (the_attendee_people) {
                            attendees.push(the_attendee_people);
                            attendee_showed += 1;
                            if (attendee_showed <= MAX_ATTENDEES) {
                                if (self.avatar_model !== null) {
                                    the_title_avatar += '<img title="' + _.escape(self.all_attendees[the_attendee_people]) + '" class="o_attendee_head"  \
                                                        src="/web/image/' + self.avatar_model + '/' + the_attendee_people + '/image_small"></img>';
                                } else {
                                    if (!self.colorIsAttendee || the_attendee_people != temp_ret[self.color_field]) {
                                        var tempColor = (self.all_filters[the_attendee_people] !== undefined)
                                            ? self.all_filters[the_attendee_people].color
                                            : (self.all_filters[-1] ? self.all_filters[-1].color : 1);
                                        the_title_avatar += '<i class="fa fa-user o_attendee_head o_underline_color_' + tempColor + '" title="' + _.escape(self.all_attendees[the_attendee_people]) + '" ></i>';
                                    }//else don't add myself
                                }
                            } else {
                                attendee_other += _.escape(self.all_attendees[the_attendee_people]) + ", ";
                            }
                        }
                    );
                    if (attendee_other.length > 2) {
                        the_title_avatar += '<span class="o_attendee_head" title="' + attendee_other.slice(0, -2) + '">+</span>';
                    }
                }
            }

            if (!date_stop && date_delay) {
                var m_start = moment(date_start).add(date_delay, 'hours');
                date_stop = m_start.toDate();
            }
            var r = {
                'start': moment(date_start).toString(),
                'end': moment(date_stop).toString(),
                'title': the_title,
                'attendee_avatars': the_title_avatar,
                'allDay': (this.fields[this.date_start].type == 'date' || (this.all_day && evt[this.all_day]) || false),
                'id': evt.id,
                'recurrency': evt.recurrency,
                'attendees': attendees
            };

            r.className = '';
            if (evt.parent_id) {
                r.className = 'o_calendar_assurance '
            }
            var color_key = evt[this.color_field];
            if (!self.useContacts || self.all_filters[color_key] !== undefined) {
                if (color_key) {
                    if (typeof color_key === "object") {
                        color_key = color_key[0];
                    }
                    r.className += 'o_calendar_color_' + this.get_color(color_key);
                }
            } else { // if form all, get color -1
                r.className += 'o_calendar_color_' + (self.all_filters[-1] ? self.all_filters[-1].color : 1);
            }
            return r;
        },

        open_event: function (id, title) {
            var self = this;
            if (!this.open_popup_action) {
                var index = this.dataset.get_id_index(id);
                this.dataset.index = index;
                if (this.write_right) {
                    this.do_switch_view('form', {mode: "edit"});
                } else {
                    this.do_switch_view('form', {mode: "view"});
                }
            } else {
                var res_id = parseInt(id).toString() === id ? parseInt(id) : id;
                var evt = self.$calendar.fullCalendar('clientEvents', id);
                var recurrency = evt.length ? evt[0].recurrency : false;
                new form_common.FormViewDialog(this, {
                    res_model: this.model,
                    res_id: res_id,
                    context: this.dataset.get_context(),
                    title: title,
                    view_id: +this.open_popup_action,
                    readonly: true,
                    buttons: [
                        {
                            text: _t("Edit"), classes: 'btn-primary', close: true, click: function () {
                                self.dataset.index = self.dataset.get_id_index(id);
                                self.do_switch_view('form', {mode: "edit"});
                            }
                        },
                        {
                            text: _t("Duplicate"), close: true, disabled: recurrency, click: function () {
                                return self.dataset.call('copy', [id, {}], self.dataset.get_context()).then(function (new_id) {
                                    self.dataset.ids = self.dataset.ids.concat([new_id]);
                                    self.dataset.trigger("dataset_changed", new_id);
                                    self.dataset.index = self.dataset.get_id_index(new_id);
                                    self.do_switch_view('form', {mode: "edit"});
                                });
                            }
                        },
                        {
                            text: _t("Detach"), close: true, disabled: !recurrency, click: function () {
                                return self.dataset.call_button('action_detach_recurring_event', [id, self.dataset.get_context()]).then(function (data) {
                                    var old_index = self.dataset.get_id_index(res_id);
                                    self.dataset.ids.splice(old_index, 1);
                                    self.$calendar.fullCalendar('removeEvents', res_id);
                                    self.dataset.trigger("dataset_changed", res_id);

                                    self.dataset.ids = self.dataset.ids.concat([data.res_id]);
                                    self.dataset.trigger("dataset_changed", data.res_id);
                                    self.refresh_event(data.res_id);
                                });
                            }
                        },
                        {
                            text: _t("Detach and Confirm"), close: true, disabled: !recurrency, click: function () {
                                return self.dataset.call_button('action_detach_and_confirm_event', [id, self.dataset.get_context()]).then(function (data) {
                                    var old_index = self.dataset.get_id_index(res_id);
                                    self.dataset.ids.splice(old_index, 1);
                                    self.$calendar.fullCalendar('removeEvents', res_id);
                                    self.dataset.trigger("dataset_changed", res_id);

                                    self.dataset.ids = self.dataset.ids.concat([data.res_id]);
                                    self.dataset.trigger("dataset_changed", data.res_id);
                                    self.refresh_event(data.res_id);
                                });
                            }
                        },
                        {
                            text: _t("Detach and Edit"), close: true, disabled: !recurrency, click: function () {
                                return self.dataset.call_button('action_detach_recurring_event', [id, self.dataset.get_context()]).then(function (data) {
                                    var old_index = self.dataset.get_id_index(res_id);
                                    self.dataset.ids.splice(old_index, 1);
                                    self.$calendar.fullCalendar('removeEvents', res_id);
                                    self.dataset.trigger("dataset_changed", res_id);

                                    self.dataset.ids = self.dataset.ids.concat([data.res_id]);
                                    self.dataset.trigger("dataset_changed", data.res_id);
                                    self.dataset.index = self.dataset.get_id_index(data.res_id);
                                    self.do_switch_view('form', {mode: "edit"});
                                });
                            }
                        },
                        {
                            text: _t("Delete"), close: true, click: function () {
                                self.remove_event(res_id);
                            }
                        },

                        {text: _t("Close"), close: true}
                    ]
                }).open();
            }
            return false;
        },
        get_color: function (key) {
            if (this.color_map[key]) {
                return this.color_map[key];
            }
            // var index = (((_.keys(this.color_map).length + 1) * 5) % 24) + 1;
            var index = key;
            this.color_map[key] = index;
            return index;
        }
    });
});
