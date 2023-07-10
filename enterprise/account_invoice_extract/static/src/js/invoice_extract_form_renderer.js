/** @odoo-module **/

import InvoiceExtractBoxLayer from '@account_invoice_extract/js/invoice_extract_box_layer';
import InvoiceExtractFields from '@account_invoice_extract/js/invoice_extract_fields';

import FormRenderer from 'web.FormRenderer';

/**
 * This is the renderer of the subview that adds OCR features on the attachment
 * preview. It displays boxes that have been generated by the OCR, and those
 * boxes are grouped by field name. The OCR automatically selects a box, but
 * the user can manually selects another box. Boxes are only visible in 'edit'
 * mode.
 */
var InvoiceExtractFormRenderer = FormRenderer.extend({
    custom_events: _.extend({}, FormRenderer.prototype.custom_events, {
        active_invoice_extract_field: '_onActiveInvoiceExtractField',
        preview_attachment_validation: '_onAttachmentPreviewValidation',
        choice_ocr_invoice_extract_box: '_onChoiceOcrInvoiceExtractBox',
        click_invoice_extract_box: '_onClickInvoiceExtractBox',
        click_invoice_extract_box_layer: '_onClickInvoiceExtractBoxLayer',
        destroy_invoice_extract_box: '_onDestroyInvoiceExtractBox',
        select_invoice_extract_box: '_onSelectInvoiceExtractBox',
    }),
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);

        this._res_id = -1;
        this._invoiceExtractBoxData = [];
        this._invoiceExtractBoxLayers = [];
        var is_customer_invoice = false;
        if (this.state.context.default_move_type == 'out_invoice' || this.state.context.default_move_type == 'out_refund')
            is_customer_invoice = true;
        this._invoiceExtractFields = new InvoiceExtractFields(this, is_customer_invoice);
        this._$invoiceExtractButtons = [];
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Remove any state related to the invoice extract, such as buttons or
     * boxes. This method is called when the form is not in 'edit' mode.
     *
     * @private
     */
    _destroyInvoiceExtract: function () {
        _.invoke(this._invoiceExtractBoxLayers, 'destroy');
        this._res_id = -1;
        this._invoiceExtractBoxData = [];
        this._invoiceExtractBoxLayers = [];
        this._invoiceExtractFields.resetActive();
        if (this._$invoiceExtractButtons.length) {
            this._$invoiceExtractButtons.remove();
        }
        this._$invoiceExtractButtons = [];
    },
    /**
     * Display the invoice extract boxes on the box layers for the active field.
     *
     * @private
     */
    _displayInvoiceExtractBoxes: function () {
        var field = this._invoiceExtractFields.getActiveField();
        if (!field) {
            return;
        }
        _.each(this._invoiceExtractBoxLayers, function (boxLayer) {
            boxLayer.displayBoxes({ fieldName: field.getName() });
        });
    },
    /**
     * Called when a box or box layer interaction has been performed by the
     * user (such as selecting a new box). Usually, a field in the form view
     * should be updated with the box content after clicking on the box.
     *
     * @private
     * @param {Object} params
     * @param {any} params.fieldChangedInfo new info on the field, based on
     *   box or box layer interaction
     */
    _handleInvoiceExtractFieldChanged: function (params) {
        var fieldChangedInfo = params.fieldChangedInfo;
        var field = this._invoiceExtractFields.getActiveField();
        if (!field) {
            return;
        }
        var changes = field.handleFieldChanged({
            fieldChangedInfo: fieldChangedInfo,
            state: this.state,
        });
        if (!_.isEmpty(changes)) {
            this.trigger_up('field_changed', {
                dataPointID: this.state.id,
                changes: changes,
            });
        }
    },
    /**
     * Setup data for the invoice extract stuffs. In particular, get box data
     * and render them. Boxes are displayed on the provided page.
     *
     * @private
     * @param {$.Element} $page jQuery element corresponding to the attachment
     *   page. This is useful for the rendering of the box layer, which is
     *   handled differently whether the attachment is an image or a pdf.
     */
    _initInvoiceExtract: function ($page) {
        var self = this;
        this._res_id = this.state.res_id;
        this._rpc({
            model: 'account.move',
            method: 'get_boxes',
            args: [this.state.res_id],
        }).then(function (boxesData) {
            self._invoiceExtractBoxData = boxesData;
            self._renderInvoiceExtractBoxLayers({
                $page: $page,
            }).then(function () {
                self._displayInvoiceExtractBoxes();
            });
        });
    },
    /**
     * Render the field buttons on top of the attachment page preview, so that
     * the user can select the boxes to show for the given field.
     *
     * @private
     * @returns {Promise} resolves when all buttons are rendered
     */
    _renderInvoiceExtractButtons: function () {
        return this._invoiceExtractFields.renderButtons({
            $container: this._$invoiceExtractButtons,
        });
    },
    /**
     * Render the box layers using fetched box data and the attachment page
     * preview. Boxes data are used in order to make and render boxes, whereas
     * the page is used in order to correctly size the box layers. Also, the
     * setup of the box layers slightly differs with images and pdf, because
     * the latter uses an iframe.
     *
     * Because the iframe is created with the pdf viewer, and there is no odoo
     * bundle related to it, we cannot simply extend the bundle with SCSS
     * styles. As a work-around, the style of the boxes and box layers must be
     * defined in CSS, so that we can dynamically add this file in the header
     * of the iframe (for the case of PDF viewer).
     *
     * @private
     * @param {Object} params
     * @param {$.Element} params.$page the attachment page preview container
     */
    _renderInvoiceExtractBoxLayers: function (params) {
        var $page = params.$page;
        var boxLayer;
        var proms = [];
        //in case of img
        if ($page.hasClass('img-fluid')) {
            // Delete previous box layer(s)
            if (this._invoiceExtractBoxLayers.length > 0) {
                for (const oldBoxLayer of this._invoiceExtractBoxLayers) {
                    oldBoxLayer.destroy();
                }
            }
            boxLayer = new InvoiceExtractBoxLayer(this, {
                boxesData: this._invoiceExtractBoxData,
                mode: 'img',
                $page: $page,
            });
            proms.push(boxLayer.insertAfter($page));
            this._invoiceExtractBoxLayers = [boxLayer];
        }
        //in case of pdf
        if ($page.is('iframe')) {
            var $document = $page.contents();
            // dynamically add css on the pdf viewer
            $document.find('head').append('<link rel="stylesheet" type="text/css" href="/account_invoice_extract/static/src/css/account_invoice_extract_box_layer.css"></link>');
            var $textLayers = $document.find('.textLayer');
            for (var index = 0; index < $textLayers.length; index++) {
                var $textLayer = $textLayers.eq(index);
                var pageNum = $textLayer[0].parentElement.dataset['pageNumber'] - 1;
                var existingBoxLayer = this._invoiceExtractBoxLayers.find(function(bl) {
                    return bl._pageNum == pageNum;
                });
                if (existingBoxLayer) {
                    existingBoxLayer.setTextLayer({
                        $textLayer: $textLayer,
                    });
                    proms.push(existingBoxLayer.insertAfter($textLayer));
                }
                else {
                    boxLayer = new InvoiceExtractBoxLayer(this, {
                        boxesData: this._invoiceExtractBoxData,
                        mode: 'pdf',
                        pageNum: pageNum,
                        $buttons: this._$invoiceExtractButtons,
                        $page: $page,
                        $textLayer: $textLayer,
                    });
                    proms.push(boxLayer.insertAfter($textLayer));
                    this._invoiceExtractBoxLayers.push(boxLayer);
                }
            }
        }
        return Promise.all(proms);
    },
    /**
     * @private
     * @param {$.Element} $attachment
     */
    _startInvoiceExtract: function ($attachment) {
        var $ocrSuccess = this.$('.o_success_ocr');
        if (
            $attachment.length !== 0 &&
            $ocrSuccess.length > 0 &&
            !$ocrSuccess.hasClass('o_invisible_modifier') &&
            this.mode === 'edit'
        ) {
            // fetch boxes data for this record
            if (this._res_id != this.state.res_id) {
                this._destroyInvoiceExtract();
                this._initInvoiceExtract($attachment);
            }
            // render boxes if their data has already been fetched
            else if (this._invoiceExtractBoxData.length > 0) {
                var self = this;
                this._renderInvoiceExtractBoxLayers({
                    $page: $attachment,
                }).then(function () {
                    self._displayInvoiceExtractBoxes();
                });
            }
            // render buttons if they're not already rendered
            if (this._$invoiceExtractButtons.length == 0) {
                this._$invoiceExtractButtons = $('<div class="o_invoice_extract_buttons"/>');
                $attachment.before(this._$invoiceExtractButtons);
                this._renderInvoiceExtractButtons();
            }
        } else {
            this._destroyInvoiceExtract();
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when there is a change on active field. It should display boxes
     * related to the newly active field.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onActiveInvoiceExtractField: function (ev) {
        ev.stopPropagation();
        this._displayInvoiceExtractBoxes();
    },
    /**
     * Called when the chatter has rendered the attachment preview. In 'edit'
     * mode, it should render the invoice extract boxes and buttons.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onAttachmentPreviewValidation: function (ev) {
        ev.stopPropagation();
        var self = this;
        if (this.$attachmentPreview === undefined) {
            return;
        }
        // case pdf (iframe)
        this.$attachmentPreview.find('iframe').on("load", function () { // wait for iframe to load
            var $iframe = self.$attachmentPreview.find('iframe');
            var $iframeDoc = self.$attachmentPreview.find('iframe').contents();
            // To get pagerendered trigger_up from pdf.js, we needed to change pdf.js default option and set
            // eventBusDispatchToDOM to True
            $iframeDoc[0].addEventListener('pagerendered', function () {
                self._startInvoiceExtract($iframe);
            });
        });
        // case img
        var $documentImg = self.$attachmentPreview.find('.img-fluid');
        var $attachment = $('#attachment_img');
        if ($attachment.length && $attachment[0].complete) {
            this._startInvoiceExtract($documentImg);
        } else {
            this.$attachmentPreview.find('.img-fluid').on("load", function () {
                self._startInvoiceExtract($documentImg);
            });
        }
    },
    /**
     * Called when clicking on a box. In this case, the box should be selected,
     * and the field in the form should be updated accordingly.
     *
     * @private
     * @param {OdooEvent} ev
     * @param {account_invoice_extract.Box} ev.data.box
     */
    _onClickInvoiceExtractBox: function (ev) {
        ev.stopPropagation();
        var self = this;
        var box = ev.data.box;
        var field = this._invoiceExtractFields.getActiveField();
        if (!field) {
            return;
        }
        this._rpc({
            model: 'account.move',
            method: 'set_user_selected_box',
            args: [[this.state.res_id], box.getID()],
        }).then(function (fieldChangedInfo) {
            field.setSelectedBox(box);
            self._handleInvoiceExtractFieldChanged({
                fieldChangedInfo: fieldChangedInfo,
            });
        });
    },
    /**
     * Called when clicking on a box layer (excluding clicking on a box inside
     * the box layer). This unselects the selected box of the active field.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onClickInvoiceExtractBoxLayer: function (ev) {
        ev.stopPropagation();
        var self = this;
        var field = this._invoiceExtractFields.getActiveField();
        if (!field) {
            return;
        }
        var box = field.getSelectedBox();
        if (!box) {
            return;
        }
        field.unselectBox();
        this._rpc({
            model: 'account.move',
            method: 'remove_user_selected_box',
            args: [
                [this.state.res_id],
                box.getID()
            ],
        }).then(function (fieldChangedInfo) {
            self._handleInvoiceExtractFieldChanged({
                fieldChangedInfo: fieldChangedInfo,
            });
        });
    },
    /**
     * Called by the box that has been chosen by the OCR. Notify the
     * corresponding field that tracks selected boxes. This is useful in order
     * to determine which box should be selected. Indeed, an OCR chosen box
     * without any user-selected box should be marked as selected.
     *
     * @private
     * @param {OdooEvent} ev
     * @param {account_invoice_extract.Box} ev.data.box
     */
    _onChoiceOcrInvoiceExtractBox: function (ev) {
        ev.stopPropagation();
        var box = ev.data.box;
        var field = this._invoiceExtractFields.getField({
            name: box.getFieldName(),
        });
        if (!field) {
            return;
        }
        field.setOcrChosenBox(box);
    },
    /**
     * Called when a box is destroyed. This occurs in particular when there
     * is a change of mode from 'edit' to 'readonly', in which box layers and
     * boxes should not appear on the attachment anymore. In this case, the
     * fields should untrack the boxes.
     *
     * @private
     * @param {OdooEvent} ev
     * @param {account_invoice_extract.Box} ev.data.box
     */
    _onDestroyInvoiceExtractBox: function (ev) {
        ev.stopPropagation();
        var box = ev.data.box;
        if (!box.isOcrChosen() && !box.isSelected()) {
            // ignore untracked boxes
            return;
        }
        var field = this._invoiceExtractFields.getField({
            name: box.getFieldName(),
        });
        if (!field) {
            return;
        }
        field.unsetBox(box);
    },
    /**
     * Called by the box that has been selected by the user. Notify the
     * corresponding field that tracks selected boxes.
     *
     * @private
     * @param {OdooEvent} ev
     * @param {account_invoice_extract.Box} ev.data.box
     */
    _onSelectInvoiceExtractBox: function (ev) {
        ev.stopPropagation();
        var box = ev.data.box;
        var field = this._invoiceExtractFields.getField({
            name: box.getFieldName(),
        });
        if (!field) {
            return;
        }
        field.setSelectedBox(box);
    },
});

export default InvoiceExtractFormRenderer;
