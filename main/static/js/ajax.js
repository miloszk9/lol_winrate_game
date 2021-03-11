$(document).ready(function(){
    $(".game_btn").click(function(){
        $.ajax({
            url: '',
            type: 'GET',
            data: {
                button_value: $(this).val(),
                champ1_name: $("#champ1_name").text(),
                champ1_role: $("#champ1_role").text(),
                champ2_name: $("#champ2_name").text(),
                champ2_role: $("#champ2_role").text()
            },
            success: function(response){
                if (response.finish == false){
                    $("#score").text(response.score),
                    
                    $("#champ1_name").text($("#champ2_name").text()),
                    $("#champ1_role").text($("#champ2_role").text()),
                    $("#champ1_win").text(response.champ1_win),
                    
                    $("#champ2_name").text(response.new_champ[0]),
                    $("#champ2_role").text(response.new_champ[1]),

                    $("#champ1_img")[0].src = $("#champ2_img")[0].src,
                    $("#champ2_img")[0].src = $("#champ2_img")[0].src.split('img/')[0] + "img/" + response.new_champ[0].replaceAll(" ", "_") + ".jpg"
                }else{
                    // Game is finished
                    $("#game").remove(),
                    $("#div_score").append('<a href="/"><button class="btn btn-success">Play again!</button></a>')
                }
            },
            error: function(){
                $("#finish").text("An error has occured!")
            }
        });
    });
});