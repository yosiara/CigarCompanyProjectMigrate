/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { Store } from "@mail/core/common/store_service";
import { patch } from "@web/core/utils/patch";

/** @type {import("models").Store} */
const storeServicePatch = {
    setup() {
        super.setup();
        // Almacén local para caché de empleados ICT
        this.ictEmployees = {};
    },

    async getChat(person) {
        const { employeeId } = person;
        if (!employeeId) {
            return super.getChat(person);
        }

        // Verificar si ya tenemos la información en caché
        let employee = this.ictEmployees[employeeId];
        if (!employee) {
            this.ictEmployees[employeeId] = { id: employeeId };
            employee = this.ictEmployees[employeeId];
        }

        // Si aún no hemos verificado si tiene user_id, lo consultamos
        if (!employee.user_id && !employee.hasCheckedUser) {
            employee.hasCheckedUser = true;
            const [employeeData] = await this.env.services.orm.silent.read(
                "ict.employee",
                [employee.id],
                ["user_id", "user_partner_id"],
                { context: { active_test: false } }
            );

            if (employeeData) {
                // user_id es un many2one -> [id, name]
                employee.user_id = employeeData.user_id?.[0];
                
                // Obtener user_id desde el empleado relacionado (hr.employee)
                if (employee.user_id) {
                    let user = this.users[employee.user_id];
                    if (!user) {
                        this.users[employee.user_id] = { id: employee.user_id };
                        user = this.users[employee.user_id];
                    }

                    // Obtener partner_id
                    if (!user.partner_id) {
                        const [userData] = await this.env.services.orm.silent.read(
                            "res.users",
                            [employee.user_id],
                            ["partner_id"],
                            { context: { active_test: false } }
                        );
                        if (userData) {
                            user.partner_id = userData.partner_id[0];
                            this.Persona.insert({
                                displayName: userData.partner_id[1],
                                id: userData.partner_id[0],
                                type: "partner",
                            });
                        }
                    }
                }
            }
        }

        if (!employee.user_id) {
            this.env.services.notification.add(
                _t("You can only chat with employees that have a dedicated user."),
                { type: "info" }
            );
            return;
        }

        // Una vez que tenemos el user_id, llamamos al método original con { userId }
        return super.getChat({ userId: employee.user_id });
    },
};

patch(Store.prototype, storeServicePatch);