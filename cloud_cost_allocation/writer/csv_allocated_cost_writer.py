'''
Created on 21.04.2022

@author: marc.diensberg
'''

from cloud_cost_allocation.cost_items import Config, ServiceInstance
from cloud_cost_allocation.writer.base_writer import GenericWriter

from cloud_cost_allocation.utils import utils


class CSV_AllocatedCostWriter(GenericWriter):
    '''
    classdocs
    '''

    def __init__(self, service_instances: dict[ServiceInstance], config: Config):
        super().__init__(service_instances, config)

    def get_headers(self) -> list[str]:

        # Column order is historical

        # Initialize
        headers = [
            'Date',
            'Service',
            'Instance',
            'Tags',
            ]

        # Add amounts
        headers.extend(self.config.amounts)

        # Add service product amounts
        for amount in self.config.amounts:
            headers.extend(['ServiceProduct' + amount])

        # Add provider info
        headers.extend([
            'Currency',
            'ProviderService',
            'ProviderInstance',
            'ProviderTagSelector',
            'ProviderCostAllocationType',
            ])

        # Add allocation keys
        headers.extend(self.config.allocation_keys)

        # Add provider info
        headers.extend([
            'ProviderCostAllocationCloudTagSelector',
            'Product',
            ])

        # Add product amounts
        for amount in self.config.amounts:
            headers.extend(['Product' + amount])

        # Add dimensions
        headers.extend(self.config.dimensions)

        # Add provider meters
        if self.config.nb_provider_meters:
            for i in range(1, self.config.nb_provider_meters + 1):
                headers.extend(['ProviderMeterName%s' % i])
                headers.extend(['ProviderMeterUnit%s' % i])
                headers.extend(['ProviderMeterValue%s' % i])

        # Add product dimensions
        if self.config.nb_product_dimensions:
            for i in range(1, self.config.nb_product_dimensions + 1):
                headers.extend(['ProductDimensionName%s' % i])
                headers.extend(['ProductDimensionElement%s' % i])

        # Add product meters
        if self.config.nb_product_meters:
            for i in range(1, self.config.nb_product_meters + 1):
                if i == 1:
                    headers.extend(['ProductMeterName'])
                    headers.extend(['ProductMeterUnit'])
                    headers.extend(['ProductMeterValue'])
                else:
                    headers.extend(['ProductMeterName%s' % i])
                    headers.extend(['ProductMeterUnit%s' % i])
                    headers.extend(['ProductMeterValue%s' % i])

        return headers

    def export_item_base(self, cost_item, service_instance) -> dict[str]:

        # Initialize
        data = {}

        # Add basic cost item data
        data['Date'] = cost_item.date_str
        data['Service'] = cost_item.service
        data['Instance'] = cost_item.instance
        data['Tags'] = utils.serialize_tags(cost_item.tags)
        data['Currency'] = cost_item.currency

        # Add dimensions
        for dimension_key, dimension_value in cost_item.dimensions.items():
            data[dimension_key] = dimension_value

        # Add amounts
        index = 0
        for amount in self.config.amounts:
            data[amount] = str(cost_item.amounts[index])
            index += 1

        # Add service product amounts
        index = 0
        for amount in self.config.amounts:
            data['ServiceProduct' + amount] = str(cost_item.get_unallocated_product_amount(index))
            index += 1

        return data


    def export_item_consumer(self, cost_item, service_instance) -> dict[str]:

        # Common export
        data = self.export_item_base(cost_item, service_instance)

        # Provider service
        data['ProviderService'] = cost_item.provider_service

        # Provider instance
        data['ProviderInstance'] = cost_item.provider_instance

        # Provider tag selector
        data['ProviderTagSelector'] = cost_item.provider_tag_selector

        # Provider cost allocation type
        data['ProviderCostAllocationType'] = cost_item.provider_cost_allocation_type

        # Provider cost allocation keys
        index = 0
        for allocation_key in self.config.allocation_keys:
            data[allocation_key] = cost_item.allocation_keys[index]
            index += 1

        # Provider cost allocation cloud tag selector
        data['ProviderCostAllocationCloudTagSelector'] = cost_item.provider_cost_allocation_cloud_tag_selector

        # Provider meters
        if self.config.nb_provider_meters:
            for i in range(1, self.config.nb_provider_meters + 1):
                meter = cost_item.provider_meters[i-1]
                data['ProviderMeterName%s' % i] = meter.name
                data['ProviderMeterUnit%s' % i] = meter.unit
                if meter.name:
                    data['ProviderMeterValue%s' % i] = str(meter.value)

        # Product
        data['Product'] = cost_item.product
        if cost_item.product:

            # Product dimensions
            if self.config.nb_product_dimensions:
                for i in range(1, self.config.nb_product_dimensions + 1):
                    product_dimension = cost_item.product_dimensions[i-1]
                    data['ProductDimensionName%s' % i] = product_dimension.name
                    data['ProductDimensionElement%s' % i] = product_dimension.element

            # Product meters
            if self.config.nb_product_meters:
                for i in range(1, self.config.nb_product_meters + 1):
                    meter = cost_item.product_meters[i-1]
                    if i == 1:
                        data['ProductMeterName'] = meter.name
                        data['ProductMeterUnit'] = meter.unit
                        if meter.name:
                            data['ProductMeterValue'] = str(meter.value)
                    else:
                        data['ProductMeterName%s' % i] = meter.name
                        data['ProductMeterUnit%s' % i] = meter.unit
                        if meter.name:
                            data['ProductMeterValue%s' % i] = str(meter.value)

            # Product amounts
            index = 0
            for amount in self.config.amounts:
                data['Product' + amount] = str(cost_item.product_amounts[index])
                index += 1

        return data
