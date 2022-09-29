import test_batches
import test_allocate

if __name__ == '__main__':
    test_batches.test_allocating_to_a_batch_reduces_the_available_quantity()
    test_batches.test_can_allocate_if_available_equal_to_required()
    test_batches.test_can_allocate_if_available_greater_than_required()
    test_batches.test_can_allocate_if_available_smaller_than_required()
    test_batches.test_can_not_allocate_if_skus_do_not_match()
    test_batches.test_allocation_is_idempotent()

    test_allocate.test_returns_allocated_batch_ref()
    test_allocate.test_prefers_earlier_batches()
    test_allocate.test_prefers_current_stock_batches_to_shipments()
    test_allocate.test_raises_out_of_stock_exception_if_cannot_allocate()


