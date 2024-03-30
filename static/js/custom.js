
$(document).ready(function(){
    $(".add-to-cart-btn").on("click", function(){
    
        let this_val = $(this)
        let index = this_val.attr("data-index")
        let quantity = $(".product-quantity-" + index).val();
        let product_title = $(".product-title-" + index).val();
        let product_id = $(".product-id-" + index).val();
        let product_price = $(".product-price-" + index).val();
        let product_price_wo_gst = $(".product-price-wo-gst-" + index).val();
        let gst_rate = $(".gst_rate-" + index).val();
        let product_sku = $(".product-sku-" + index).val();
        let product_image = $(".product-image-" + index).val();
    
        console.log("Quantity:", quantity);
        console.log("Title:", product_title);
        console.log("Price:", product_price);
        console.log("Price Without Gst:", product_price_wo_gst);
        console.log("gst_rate:", gst_rate);
        console.log("ID:", product_id);
        console.log("Image:", product_image);
        console.log("Sku:", product_sku);
        console.log("Index:", index);
        console.log("Current Element:", this_val);

        $.ajax({
            url: '/add-to-cart',
            data : {
                'id': product_id,
                'image': product_image,
                'qty': quantity,
                'title': product_title,
                'price': product_price,
                'price_wo_gst': product_price_wo_gst,
                'gst_rate': gst_rate,
                'sku' : product_sku,
            },
            dataType: 'json',
            beforeSend: function(){
                console.log("Adding Product to the cart...");
            },
            success: function(response){
                this_val.html("✓");
                console.log("Added Product to cart!");
                $(".cart-items-count").text(response.totalcartitems);
    
                // Display SweetAlert
                Swal.fire({
                  position: 'top-end',
                  icon: 'success',
                  title: 'Product has been added to your cart',
                  showConfirmButton: false,
                  timer: 1500
                });
            }
    
        })
    })
    })
    
    
    $(document).ready(function(){
        $(".delete-product").on("click", function(){
            let product_id = $(this).attr("data-product");
            let this_val = $(this);
    
            console.log("Product ID:", product_id);
    
            // Display SweetAlert confirmation dialog
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    // User confirmed the deletion, proceed with AJAX request
                    $.ajax({
                        url: "/delete-from-cart",
                        data: {
                            "id": product_id
                        },
                        dataType: "json",
                        beforeSend: function(){
                            this_val.hide();
                        },
                        success: function(response){
                            this_val.show();
                            $(".cart-items-count").text(response.totalcartitems);
                            $("#cart-list").html(response.data);
                        }
                    });
                }
            });
        });
    });
    

    $(document).ready(function(){
        $(".update-product").on("click", function(){
            let product_id = $(this).attr("data-product")
            let this_val = $(this)
            let product_quantity = $(".product-qty-"+product_id).val()
        
            console.log("Product ID:", product_id);
            console.log("Product Qty:", product_quantity);
    
            $.ajax({
                url: "/update-cart",
                data : {
                    "id": product_id,
                    "qty": product_quantity,
                },
                dataType: "json",
                beforeSend: function(){
                    this_val.hide()
                },
                success: function(response){
                    this_val.show()
                    $(".cart-items-count").text(response.totalcartitems)
                    $("#cart-list").html(response.data)
                }
            })
        })
    })

    