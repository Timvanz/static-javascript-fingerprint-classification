/* ****************************************************************************
 *
 * Deriving Member Expressions and Variables
 *
 * Author  : Tim van Zalingen and Sjors Haanen
 * Date    : 25 Januari 2017
 * Course  : Research Project 1 (RP1)
 * Filename: scope.js
 *
 * This script takes a JavaScript file as input argument. For each member
 * expression (i.e. vara.varb), all previous assignments are traversed to
 * output the most complete name of the variable. This is done to see what
 * exact properties are called from what exact object.
 * 
 * Example:
 *   var nav = navigator;
 *   var np = nav.plugins;
 *   ...
 * Output:
 *   navigator.plugins
 *   ...
 *
 * Workings: The JavaScript file is parsed to an Abstract Syntax Tree (AST).
 *   This AST is traversed and a scope table is kept. For each member
 *   expression found, the scope table is used to derive the full written
 *   member expression.
 * 
 * Requirements: NodeJS, file-system, esprima and estraverse
 *
 * ***************************************************************************/

/* file-system (for i/o), esprima (for creating the AST), estraverse (AST
 * traversal) and walk (recursively walk directory for files) are required. */
var fs = require('fs');
var esprima = require('esprima');
var estraverse = require('estraverse');
var walk = require('walk');

/* In output, the result for each file is stored. scopeChain is the an array
 * containing dictionaries, with each dictionary a scope level. */
var output = "";
var scopeChain = [];

/* The walk should not follow (sym)links to other directories. */
options = {
    followLinks: false
};

/* The folder to be walked for member expression expansion is provided as
 * argument. */
var dir = process.argv[2];
var walker = walk.walk(dir, options);

/* This event handles what the walker should do when running into a file.
 * The file is opened if it is a ".dob" file, the memberExpressionExpansion is
 * run on that file and it is saved to the same file but appended with ".exp".
 */
walker.on('file', function (root, fileStats, next) {
    var filename = fileStats.name;
    var filepath = root + '/' + filename;
    /* If ".dob" file expand and save. */
    if (filename.substr(filename.length - 4) == '.dob') {
        console.log(filepath + " expanded");
        output = memberExpressionExpansion(filepath);
        if (output != null) {
        fs.writeFile(filepath + '.exp', output, function(err) {
            if(err) {
                return console.log(err);
            }

        });
        }
    }
    /* Move to next file or directory. */
    next();
});

/* When entering a directory, the walker should simply continue and do no
 * action. */
walker.on("directories", function (root, dirStatsArray, next) {
    next();
});

function memberExpressionExpansion(filepath) {
    /* A new file is considered, so the output should be reset. */
    output = "";
    /* The file is taken from the first command line argument. This file is
     * used to build the AST. */
     try{
    var ast = esprima.parse(fs.readFileSync(filepath));
    }
    catch(err){
        return null;
    }
    /* scopeChain is used to store the scope in multiple levels. */
    scopeChain = [];

    /* The enter and leave functions are used for the traversal. */
    estraverse.traverse(ast, {
        enter: enter,
        leave: leave
    });
    return output;
}

/* This function either returns an Identifer, MemberExpression as. */
function getIdentifierOrName(node) {
    var name = undefined;
    /* If an Identifier is encountered, its name can simply be returned.
     * Otherwise if a MemberExpression is encountered, both sides need to be
     * converted to strings seperately concatenated. */
    if (node.type === "Identifier") {
        name = node.name;
    }
    else if (node.type === "MemberExpression") {
        /* The object side of a MemberExpression is an Identifier or another
         * MemberExpression, so therefore this function is called recursively.
         */
        name = getIdentifierOrName(node.object) + '.' + node.property.name;
    }
    return name;
}

/* This function is called when a variable needs to be added to the scope. */
function addToScope(node) {
    /* The variable is added to the current scope (or the last level added to
     * the scopeChain). identifier is that of the variable, name the init part
     * (null if no init). */
    var currentScope = scopeChain[scopeChain.length - 1];
    /* If a node is declared with "var" or else assigned globally. */
    if (node.id != null) {
        var identifier = node.id.name;
        var name = undefined;
        /* If there is an init section, it is added as name (dict value). */
        if (node.init != null) {
            /* If it is an Identifier, the name of the Identifier is simply
             * added. If it is a MemberExpression, the whole expression is
             * added as name. */
            name = getIdentifierOrName(node.init);
        }
        /* The identifier with its corresponding init value is added to the
         * scope */
        currentScope[identifier] = name;
    }
    else if (node.left != null && node.right != null) {
        /* The left side of the expression as identifier and right side as
         * assigned name are added to the current scope. */
        var identifier = node.left.name;
        var name = getIdentifierOrName(node.right);
        currentScope[identifier] = name;
    }
}

/* Function if a node is entered. A VariableDeclarator and AssignmentExpression
 * should be added/updated to/in the scope. A MemberExpression shoud be
 * expanded if possible. */
function enter(node){
    if (createsNewScope(node)){
        scopeChain.push({});
    }
    if (node.type === 'VariableDeclarator'){
        addToScope(node);
    }
    else if (node.type === 'AssignmentExpression') {
        assignVarValue(node.left.name, getIdentifierOrName(node.right), node, scopeChain);
    }
    else if (node.type === 'MemberExpression') {
        /* Added to output, to allow it to be written to a file after the full
         * AST traversal. */
        output += isVarDefined(getIdentifierOrName(node.object), scopeChain, []) + '.' + node.property.name + '\n';
    }
}

/* If a node is left that would have created a new scope, the last scope added
 * to the scopeChain should be popped. */
function leave(node){
    if (createsNewScope(node)){
        scopeChain.pop();
    }
}

/* This function will check whether a variable in the scope (object in the
 * MembexExpression) exists. If so, its value will be returned or, if possible,
 * a next variable that defines the the found variable as something else will
 * be considered. */
function isVarDefined(varname, scopeChain, previous){
    /* rest is the property (or properties) part of a MemberExpression if
     * applicable. */
    var rest = '';
    if (varname == null) {
        return undefined;
    }
    /* If it is a MemberExpression, only the first object should be considered
     * and the rest is kept in rest to be appended to the result. */
    if (varname.indexOf('.') >= 0) {
        rest = '.' + varname.slice(varname.indexOf('.') + 1);
        varname = varname.split('.')[0];
    }
    /* The whole scopeChain is searched for varname. If found, the value is
     * returned to expand the variable. */
    for (var i = 0; i < scopeChain.length; i++){
        var scope = scopeChain[i];
        if (varname in scope){
            var returnValue = scope[varname];
            if (returnValue != undefined) {
                /* The in the scopeChain found variable should not be exactly
                 * the same or previously found. (prevent loops or infite
                 * recursion) */
                if (scope != null && scope[varname] != null && typeof(scope[varname]) == "string" && scope[varname].split('.')[0] != varname && !(previous.indexOf(scope[varname].split('.')[0]) > -1)) {
                    previous.push(scope[varname].split('.')[0]);
                    /* If a next variable that expands varname is found, that
                     * variable should used from now on and thus is returned.
                     * Any expansion or translation of the next varname is
                     * found in this recursive step. */
                    var next = isVarDefined(scope[varname].split('.')[0], scopeChain, previous);
                    if (next != undefined) {
                        returnValue = scope[varname].replace(scope[varname].split('.')[0], next);
                    }
                }
            return returnValue + rest;
            }
        }
    }
    return varname + rest;
}

/* This function changes the value of a variable in the current scope or if it
 * does not exist it should be added to the scope. */
function assignVarValue(varname, value, node, scopeChain){
    var currentScope = scopeChain[scopeChain.length - 1];
    if (varname in currentScope){
        currentScope[varname] = value;
        return;
    }
    addToScope(node);
}

/* Checks whether a function enters a new scope or not. */
function createsNewScope(node){
    return node.type === 'FunctionDeclaration' ||
        node.type === 'FunctionExpression' ||
        node.type === 'Program';
}
