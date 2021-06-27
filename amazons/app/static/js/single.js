const boardwidth = 6;
const sq_width = 60;

var turn = localStorage.getItem("turn")

const states = [
    'white_selects', 'white_moves', 'white_shoots',
    'black_selects','black_moves', 'black_shoots'];

function create2darray(m, n, fill_value = undefined) {
	// Function that creates an m x n array.
	// m rows, n cols, fill with fill_value
	mat = [];
	for (i=0; i < m; i++) {
		rows = [];
		for (j=0; j < n; j++) {
			rows.push(fill_value);
		}
		mat.push(rows);
	}
	return mat;
}

function DrawAmazon(x, y, w, color) {
    if (color == 'Black Amazon') {
        fill(0);
    }
    else {
        fill(255);
    }
    stroke(0);
    strokeWeight(1);
    rect(x + 0.2 * w, y + 0.85 * w, w * 0.6, w * 0.08);
    rect(x + 0.2 * w, y + 0.78 * w, w * 0.6, w * 0.10);
    rect(x + 0.3 * w, y + 0.60 * w, w * 0.4, w * 0.15);
    triangle(
        x + 0.1 * w, y + 0.40 * w,
        x + 0.25 * w, y + 0.77 * w,
        x + 0.15 * w, y + 0.77 * w);
    triangle(
        x + 0.2 * w, y + 0.30 * w,
        x + 0.3 * w, y + 0.58 * w,
        x + 0.2 * w, y + 0.58 * w);
    triangle(
        x + 0.35 * w, y + 0.20 * w,
        x + 0.32 * w, y + 0.58 * w,
        x + 0.42 * w, y + 0.58 * w);
    triangle(
        x + 0.5 * w, y + 0.10 * w,
        x + 0.55 * w, y + 0.58 * w,
        x + 0.45 * w, y + 0.58 * w);
    triangle(
        x + 0.65 * w, y + 0.20 * w,
        x + 0.58 * w, y + 0.58 * w,
        x + 0.68 * w, y + 0.58 * w);
    triangle(
        x + 0.8 * w, y + 0.30 * w,
        x + 0.8 * w, y + 0.58 * w,
        x + 0.7 * w, y + 0.58 * w);
    triangle(
        x + 0.9 * w, y + 0.40 * w,
        x + 0.85 * w, y + 0.77 * w,
        x + 0.75 * w, y + 0.77 * w);
}

function SquareSelecter(mouse_x, mouse_y) {
    /* Square selecter. Returns the square which is pressed after a
    mousepressed event.*/
    // Checks wether a square is selected. Returns the selected square.
    let selection;
    for (i=0; i < boardwidth; i++) {
        for (j=0; j < boardwidth; j++) {
            if (board.matrix[i][j].x < mouse_x &&
                board.matrix[i][j].x + board.matrix[i][j].width > mouse_x &&
                board.matrix[i][j].y < mouse_y &&
                board.matrix[i][j].y + board.matrix[i][j].width > mouse_y) {
                    selection = [i, j];
            }
        }
    }
    if (selection) {
        return selection;
    }
    else {
        return [undefined, undefined];
    };
}

function ShowOptions(board, i, j){
    /*
    Shows all available options for a selected square in a board object.
    Options are squares that can be reached horizontally, vertically
    and diagonally from the selected square, without being obstructed
    by a flaming square or another amazon.
    */
   let options = []

   // Check above
   for (row = i - 1; row > -1; row--) {
       if (board.matrix[row][j].state == '0') {
           options.push([row, j])
       }
       else {
           break;
       }
   }

   // Check below
   for (row = i + 1; row < boardwidth; row++){
       if (board.matrix[row][j].state == '0') {
           options.push([row, j])
       }
       else {
           break;
       }
   }

    // Check left
    for (col = j - 1; col > -1; col--) {
        if (board.matrix[i][col].state == '0') {
            options.push([i, col])
        }
        else {
            break;
        }
    }

    // Check right
    for (col = j + 1; col < boardwidth; col++) {
        if (board.matrix[i][col].state == '0') {
            options.push([i, col])
        }
        else {
            break;
        }
    }

    let space_left = j;
    let space_right = boardwidth - j - 1;
    let space_up = i;
    let space_down = boardwidth - i - 1;


    // Check upleft
    for (offset = 1; offset <= min(space_left, space_up); offset++) {
        if (board.matrix[i - offset][j - offset].state == '0') {
            options.push([i - offset, j - offset]);
        }
        else {
            break;
        }
    }

    // Check upright
    for (offset = 1; offset <= min(space_right, space_up); offset++) {
        if (board.matrix[i - offset][j + offset].state == '0') {
            options.push([i - offset, j + offset]);
        }
        else {
            break;
        }
    }

    // Check downleft
    for (offset = 1; offset <= min(space_left, space_down); offset++) {
        if (board.matrix[i + offset][j - offset].state == '0') {
            options.push([i + offset, j - offset]);
        }
        else {
            break;
        }
    }

    // Check downright
    for (offset = 1; offset <= min(space_right, space_down); offset++) {
        if (board.matrix[i + offset][j + offset].state == '0') {
            options.push([i + offset, j + offset]);
        }
        else {
            break;
        }
    }

    return options;
}

class Board {
    constructor(
        x, y, w, h, sq_width, state, n_amazons, end
        ) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.sq_width = sq_width;
        this.state = state;
        this.n_amazons = n_amazons;
        this.m = h / sq_width; // Maximum square vertically
        this.n = w / sq_width; // Maximum square horizontally

        // Create an m x n matrix
        this.matrix = create2darray(this.m, this.n, '0');
    }

    fill_board() {
        /* Fills the board with squares.*/
        for (let i = 0; i < this.n; i++) {
            for (let j = 0; j < this.m; j++) {
                if ((i + j) % 2 != 0) {
                    var square_color = "Black";
                }
                else {
                    var square_color = "White";
                }
                this.matrix[i][j] = new Square(
                    this.x + i * this.sq_width,
                    this.y + j * this.sq_width,
                    '0',
                    this.sq_width,
                    square_color
                );
            }
        }

        // Fill the board with n_amazons for each side.
        var white_side = [];
        var black_side = [];
        for (let i=0; i < boardwidth; i++) {
            white_side.push([0, i]);
            white_side.push([i, boardwidth-1]);
        }
        for (let i=boardwidth-1; i>-1; i--) {
            black_side.push([boardwidth-1, i]);
            black_side.push([i, 0]);
        }
        const stepsize = Math.floor(black_side.length/this.n_amazons)
        for (let i=0; i < this.n_amazons; i++){
            var white_amazon_square = white_side[stepsize * i];
            var black_amazon_square = black_side[stepsize * i];
            this.matrix[
                white_amazon_square[0]][white_amazon_square[1]
            ].state = 'White Amazon';
            this.matrix[
                black_amazon_square[0]][black_amazon_square[1]
            ].state = 'Black Amazon';
        }
        console.log("Board Filled with:")
        console.log(this.matrix)
    }

    reset(state) {
        for (let i = 0; i < boardwidth; i++) {
            for (let j = 0; j < boardwidth; j++) {
                board.matrix[i][j].selected = false;
                board.matrix[i][j].option = false;
                board.state = state;
            }
        }
    }

    show_options(i, j, draw) {
        /*
        Shows all available options for a selected square in a board object.
        Options are squares that can be reached horizontally, vertically
        and diagonally from the selected square, without being obstructed
        by a flaming square or another amazon.
        */
        let options = [];

        // Check above
        for (let row = i - 1; row > -1; row--) {
            if (this.matrix[row][j].state == '0') {
                options.push([row, j])
            }
            else {
                break;
            }
        }

        // Check below
        for (let row = i + 1; row < boardwidth; row++){
            if (this.matrix[row][j].state == '0') {
                options.push([row, j])
            }
            else {
                break;
            }
        }

        // Check left
        for (let col = j - 1; col > -1; col--) {
            if (this.matrix[i][col].state == '0') {
                options.push([i, col])
            }
            else {
                break;
            }
        }

        // Check right
        for (let col = j + 1; col < boardwidth; col++) {
            if (this.matrix[i][col].state == '0') {
                options.push([i, col])
            }
            else {
                break;
            }
        }

        let space_left = j;
        let space_right = boardwidth - j - 1;
        let space_up = i;
        let space_down = boardwidth - i - 1;


        // Check upleft
        for (let offset = 1; offset <= min(space_left, space_up); offset++) {
            if (this.matrix[i - offset][j - offset].state == '0') {
                options.push([i - offset, j - offset]);
            }
            else {
                break;
            }
        }

        // Check upright
        for (let offset = 1; offset <= min(space_right, space_up); offset++) {
            if (this.matrix[i - offset][j + offset].state == '0') {
                options.push([i - offset, j + offset]);
            }
            else {
                break;
            }
        }

        // Check downleft
        for (let offset = 1; offset <= min(space_left, space_down); offset++) {
            if (this.matrix[i + offset][j - offset].state == '0') {
                options.push([i + offset, j - offset]);
            }
            else {
                break;
            }
        }

        // Check downright
        for (let offset = 1; offset <= min(space_right, space_down); offset++) {
            if (this.matrix[i + offset][j + offset].state == '0') {
                options.push([i + offset, j + offset]);
            }
            else {
                break;
            }
        }

        if (draw) {
            options.forEach(option => {
                this.matrix[option[0]][option[1]].option = true;
            });
        }

        return options;
    }

    selectedAmazon() {
        /*
        Function that returns (i, j) of the selected Amazon.
        */
        var selected = undefined;

        for (let i = 0; i < boardwidth; i++){
            for (let j = 0; j < boardwidth; j++) {
                if (board.matrix[i][j].selected == true){
                    selected = [i, j]
                }
            }
        }
        console.log("selected", selected)
        return selected;
    }

    moveAmazon(from_i, from_j, to_i, to_j) {
        /*
        Moves a selected amazon to square from (i, j) to (i, j)
        */
        // for (i=0; i < boardwidth; i++) {
        //     for (j=0; j < boardwidth; j++) {
        //         if (board.matrix[i][j].selected == true) {
        //             let amazon_color = board.matrix[i][j].state;
        //             board.matrix[i][j].state = "0"; // remove the old amazon.
        //             board.matrix[target_i][target_j].state = amazon_color;
        //             board.matrix[i][j].option = false;
        //         }
        //     }
        // }

        let amazon_color = board.matrix[from_i][from_j].state;
        board.matrix[from_i][from_j].state = "0";
        board.matrix[to_i][to_j].state = amazon_color;
        // for (i=0; i < boardwidth; i++) {
        //     for (j=0; j < boardwidth; j++) {
        //         board.matrix[i][j].option = false;
        //     }
        // }
    }

    gameEnded() {
        var ended = false;

        let whiteStuck = !board.hasMoves("White Amazon");
        let blackStuck = !board.hasMoves("Black Amazon");
        if (whiteStuck || blackStuck) {
            ended = true;
            if (whiteStuck && blackStuck) {
                board.state = "Game Drawn"
            }
            else if (whiteStuck) {
                board.state = "Black Wins"
            }
            else if (blackStuck) {
                board.state = "White Wins"
            }
        }

        return ended;
    }

    hasMoves(color) {
        var hasMoves = false;

        /* Loop over all fields, checking if there is a movable piece there */
        for (let i = 0; i < this.m; i++) {
            for (let j = 0; j < this.n; j++) {
                if (this.matrix[i][j].state == color) {
                    let options = this.show_options(i, j, false);

                    if (options.length > 0) {
                        hasMoves = true;
                        break;
                    }
                }
            }

            if (hasMoves) {
                break;
            }
        }

        return hasMoves;
    }

    show() {
        /* Shows the board on the canvas.*/
        for (let i = 0; i < this.m; i++) {
            for (let j = 0; j < this.n; j++) {
                this.matrix[i][j].show()
            }
        }
    }
}

class Square {
    constructor(x, y, state, width, color) {
        this.x = x;
        this.y = y;
        this.state = state;
        this.width = width;
        this.color = color;
        this.selected = false;
        this.option = false;
    }

    show() {
        stroke(0);
        strokeWeight(2);
        if (this.state == "F") {
            fill(178, 34, 34, 100); // red
        }
        else if (this.selected == true) {
            fill(255, 218, 185); // pinkish
        }
        else if (this.color == 'Black') {
            fill(139, 69, 19); // black
        }
        else {
            fill(255, 248, 220); // white
        }
        rect(this.x, this.y, this.width, this.width);

        if (this.state == "White Amazon" || this.state ==  "Black Amazon") {
            DrawAmazon(this.x, this.y, this.width, this.state);
        }

        if (this.option == true) {
            noStroke();
            fill(85, 107, 47, 100); // Green
            // fill(178, 34, 34, 100); // Red
            ellipseMode(CENTER);
            ellipse(this.x + 0.5 * this.width,
                this.y + 0.5 * this.width, this.width/5, this.width/5);
        }
    }
}

function mousePressed() {
    let [i, j] = SquareSelecter(mouseX, mouseY);

    console.log(board.state);
    if (i != undefined) {

        // Prepare to send move to server
        let state = board.state;
        const data = {
            "game_id": game_id,
            "move_type": board.state,
            "from_position": undefined,
            "to_position": [i, j]
        };

        // White Selects.
        if (board.state == "white_selects") {
            // If an option gets pressed we move there.
            if (board.matrix[i][j].option == true) {
                let [selected_amazon_i, selected_amazon_j] = board.selectedAmazon();
                board.moveAmazon(selected_amazon_i, selected_amazon_j, i, j);
                data["from_position"] = [selected_amazon_i, selected_amazon_j];
                board.reset("white_shoots"); // reset the board to white_shoots.
                // Prepare shooting
                board.matrix[i][j].selected = true;
                board.show_options(i, j, true);
            }
            // White Amazon gets pressed.
            else if (board.matrix[i][j].state == "White Amazon") {
                // Amazon was already selected -> deselect
                if (board.matrix[i][j].selected == true) {
                    board.reset("white_selects");
                }
                // Amazon was not yet selected -> select
                else {
                    board.reset("white_selects");
                    board.matrix[i][j].selected = true;
                    board.show_options(i, j, true);
                }
            }
            // Anything else happens.
            else {
                board.reset("white_selects");
            }
        }

        // White Shoots
        else if (board.state == "white_shoots") {
            // shoot arrow
            if (board.matrix[i][j].option == true) {
                board.matrix[i][j].state = "F"; // burn the square
                turn = -1;
                board.reset("black_selects");

                // check if black or white has no moves left
                if (board.gameEnded()) {
                    const end = {
                        "game_id": game_id,
                        "uid": uid,
                        "move_type": board.state,
                        "from_position": undefined,
                        "to_position": undefined
                    };
                    sendResult(end);
                }
            } else {
                return;
            }
        }

        // Black Selects
        else if (board.state == "black_selects") {
            // If an option gets pressed we move there.
            if (board.matrix[i][j].option == true) {
                let [selected_i, selected_j] = board.selectedAmazon();
                board.moveAmazon(selected_i, selected_j, i, j);
                data["from_position"] = [selected_i, selected_j];
                board.reset("black_shoots"); // reset the board to black_shoots.
                // Prepare shooting
                board.matrix[i][j].selected = true;
                board.show_options(i, j, true);
            }
            // Black Amazon gets pressed.
            else if (board.matrix[i][j].state == "Black Amazon") {
                // Amazon was already selected -> deselect
                if (board.matrix[i][j].selected == true) {
                    board.reset("black_selects");
                }
                // Amazon was not yet selected -> select
                else {
                    board.reset("black_selects");
                    board.matrix[i][j].selected = true;
                    board.show_options(i, j, true);
                }
            }
            // Anything else happens.
            else {
                board.reset("black_selects");
            }
        }

        // Black Shoots
        else if (board.state == "black_shoots") {
            // shoot arrow
            if (board.matrix[i][j].option == true) {
                board.matrix[i][j].state = "F"; // burn the square
                turn = -1;
                board.reset("white_selects")

                // check if black or white has no moves left
                if (board.gameEnded()) {
                    const end = {
                        "game_id": game_id,
                        "uid": uid,
                        "move_type": board.state,
                        "from_position": undefined,
                        "to_position": undefined
                    };
                    sendResult(end);
                }
            } else {
                return;
            }
        } else {
            console.log("Something went wrong, please try again.")
        }
    } else {
        // If board state is selects, reset otherwise don't.
        if ((board.state == "white_selects") || (board.state == "black_selects")) {
            board.reset(board.state);
        } else {
            return;
        }
    }
}

function resign() {
    const end = {
        "game_id": game_id,
        "uid": uid,
        "move_type": "Player " + uid + " resigned",
        "from_position": undefined,
        "to_position": undefined
    };
}

function setup() {
    createCanvas(boardwidth * sq_width, boardwidth * sq_width).parent('canvasHolder');
    board = new Board(
        0, 0, boardwidth * sq_width,
        boardwidth * sq_width, sq_width, state = states[0], n_amazons = 2);
    board.fill_board();
    board.show();
}

function draw() {
    board.show();
}