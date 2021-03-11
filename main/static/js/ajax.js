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
                $("#score").text(response.score),
                $("#finish").text(response.finish),
                
                $("#champ1_name").text($("#champ2_name").text()),
                $("#champ1_role").text($("#champ2_role").text()),
                $("#champ1_win").text(response.champ1_win),
                
                $("#champ2_name").text(response.new_champ[0]),
                $("#champ2_role").text(response.new_champ[1])
            },
            error: function(){
                $("#finish").text("An error has occured!")
            }
        });
    });
});