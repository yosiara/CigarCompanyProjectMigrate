import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { CalendarFilterPanel } from "@web/views/calendar/filter_panel/calendar_filter_panel";

patch(CalendarFilterPanel.prototype, {
    // Sobreescribir loadSource para agregar dominio a los partners
    async loadSource(section, request) {
        if (section.fieldName === 'partner_ids') { // Para asistentes solamente
            const resModel = this.props.model.fields[section.fieldName].relation;
            const domain = [
                ["id", "not in", section.filters.filter((f) => f.type !== "all").map((f) => f.value)],
                ["employee_ids", "!=", false], // Con empleados asociados
            ];
            const records = await this.orm.call(resModel, "name_search", [], {
                name: request,
                operator: "ilike",
                args: domain,
                limit: 8,
                context: {},
            });

            const options = records.map((result) => ({
                value: result[0],
                label: result[1],
                model: resModel,
            }));

            if (records.length > 7) {
                options.push({
                    label: _t("Search More..."),
                    action: () => this.onSearchMore(section, resModel, domain, request),
                    classList: "o_calendar_dropdown_option",
                });
            }

            if (records.length === 0) {
                options.push({
                    label: _t("No records"),
                    classList: "o_m2o_no_result",
                    unselectable: true,
                });
            }

            return options;
        }

        return super.loadSource(section, request);
    },

});