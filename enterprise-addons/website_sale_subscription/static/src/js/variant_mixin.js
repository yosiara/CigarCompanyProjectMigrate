/** @odoo-module **/

import VariantMixin from "@website_sale/js/sale_variant_mixin";
import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement } from "@web/core/utils/render";

import "@website_sale/js/website_sale";

/**
 * Update the renting text when the combination change.
 *
 * @param {Event} ev
 * @param {$.Element} $parent
 * @param {object} combination
 */
VariantMixin._onChangeCombinationSubscription = function (ev, $parent, combination) {
    if (!this.isWebsite || !combination.is_subscription) {
        return;
    }
    const parent = $parent.get(0);
    const unit = parent.querySelector(".o_subscription_unit");
    const price = parent.querySelector(".o_subscription_price") || parent.querySelector(".product_price h5");
    const pricingSelect =
        parent.querySelector(".js_main_product h5:has(.o_subscription_price)") ||
        parent.querySelector(".js_main_product select.plan_select");
    const pricingTable = document.querySelector("#oe_wsale_subscription_pricing_table");
    const addToCartButton = document.querySelector('#add_to_cart');
    if (addToCartButton) {
        addToCartButton.dataset.subscriptionPlanId = combination.pricings.length > 0 ? combination.subscription_default_pricing_plan_id : '';
    }
    if (unit) {
        unit.textContent = combination.temporal_unit_display;
    }
    if (price) {
        price.textContent = combination.subscription_default_pricing_price;
    }
    if (pricingSelect) {
        pricingSelect.replaceWith(
            renderToElement("website_sale_subscription.SubscriptionPricingSelect", {
                combination_info: combination,
            })
        );
    } else {
        // we dont find the element in the dom which means there was no pricings in the previous combination so there is no `select` or `h5` elements to replace then we append one.
        const nodeToAppend = parent.querySelector(".js_main_product div div");
        nodeToAppend.append(
            renderToElement("website_sale_subscription.SubscriptionPricingSelect", {
                combination_info: combination,
            })
        );
    }
    if (pricingTable) {
        pricingTable.replaceWith(
            renderToElement("website_sale_subscription.SubscriptionPricingTable", {
                combination_info: combination,
            })
        );
    } else {
        // we dont find the element in the dom which means there was no pricings in the previous combination so there is no `table` elements to replace then we append one.
        const nodeToAppend = document.querySelector("#product_details form");
        nodeToAppend.after(
            renderToElement("website_sale_subscription.SubscriptionPricingTable", {
                combination_info: combination,
            })
        );
    }
};

publicWidget.registry.WebsiteSale.include({
    /**
     * Update the renting text when the combination change.
     * @override
     */
    _onChangeCombination: function (){
        this._super.apply(this, arguments);
        VariantMixin._onChangeCombinationSubscription.apply(this, arguments);
    },
});

export default VariantMixin;
