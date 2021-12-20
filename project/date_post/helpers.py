def modify_img_for_multiple_imgs(post_pk, image):
    dict = {}
    dict['date_post'] = post_pk
    dict['content'] = image
    return dict
