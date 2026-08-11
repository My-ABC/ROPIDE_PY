import re
import math

def parseRopInput(input_str: str, gadgets: list, options: dict = None):
    if options is None:
        options = {}

    leftStartAddress = options.get("leftStartAddress")
    rightStartAddress = options.get("rightStartAddress")

    lines = input_str.split('\n')
    charPosInInputMap = []
    highlightLines = []
    constants = {}
    errorCount = 0
    hexChars = ''
    posInInput = 0

    deferredValuePatches = []
    deferredHighlightPatches = []

    def evalExpression(inner, constants, allowUndefinedAsDeferred=False):
        value = 0x0000
        symbol = '+'
        hasErrors = False
        deferred = False

        parts = [p for p in inner.split(' ') if p]
        for part in parts:
            if part.startswith('$'):
                constantName = part[1:]
                constantValue = constants.get(constantName)

                if constantValue is not None:
                    if symbol == '+':
                        value += constantValue
                    elif symbol == '-':
                        value -= constantValue
                    else:
                        hasErrors = True
                        break
                else:
                    if allowUndefinedAsDeferred:
                        deferred = True
                        if symbol == '+':
                            value += 0
                        elif symbol == '-':
                            value -= 0
                        else:
                            hasErrors = True
                            break
                    else:
                        hasErrors = True
                        break

                symbol = ''
            elif part == '+' or part == '-':
                if symbol == '':
                    symbol = part
                else:
                    hasErrors = True
                    break
            else:
                if not re.match(r'^-?[0-9a-fA-F]+$', part):
                    hasErrors = True
                    break

                if symbol == '+':
                    value += int(part, 16)
                elif symbol == '-':
                    value -= int(part, 16)
                else:
                    hasErrors = True
                    break
                symbol = ''

        if symbol != '':
            hasErrors = True
        elif isinstance(value, int):
            if value < 0:
                value = 0x10000 + value
            value &= 0xffff
        else:
            hasErrors = True

        return {'value': value, 'hasErrors': hasErrors, 'deferred': deferred}

    def pushHexChars(hex_str, startPosInLine, endPosInLine, repeatBytes):
        nonlocal hexChars, charPosInInputMap

        if not hex_str:
            return

        hexChars += hex_str.upper()

        for _ in range(repeatBytes):
            charPosInInputMap.append(startPosInLine)
            charPosInInputMap.append(endPosInLine)

    for lineIndex, line in enumerate(lines):
        lineStartPosInInput = posInInput
        spans = []

        def pushSpan(type_name, content):
            spans.append({'type': type_name, 'content': content})

        i = 0
        while i < len(line):
            char = line[i]
            charPosInInput = lineStartPosInInput + i

            # 注释 //...
            if char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                commentContent = line[i:]
                pushSpan('comment', commentContent)
                break

            # 常量 $a = 0x...; 或 $a = ...;
            elif char == '$':
                j = i + 1
                while j < len(line) and line[j] != ';':
                    j += 1

                hasSemicolon = j < len(line) and line[j] == ';'
                constantContent = line[i: j + 1 if hasSemicolon else j]

                if hasSemicolon:
                    constantStr = re.sub(r'\s+', '', line[i + 1:j])
                    parts = constantStr.split('=')

                    if len(parts) == 2:
                        try:
                            intValue = int(parts[1], 16)
                        except ValueError:
                            intValue = float('nan')

                        if re.match(r'^-?[0-9a-fA-F]+$', parts[1]) and not math.isnan(intValue):
                            if intValue < 0:
                                intValue = 0x10000 + intValue
                            intValue &= 0xffff
                        else:
                            errorCount += 1
                            pushSpan('constant,value,warning', constantContent)
                            i = j + 1
                            continue

                        if constants.get(parts[0]) is not None:
                            errorCount += 1
                            pushSpan('constant,name,warning', constantContent)
                            i = j + 1
                            continue

                        constants[parts[0]] = intValue

                    partsForHighlight = re.split(r'(\s*=\s*)', constantContent)
                    if len(partsForHighlight) == 3:
                        pushSpan('constant,name', partsForHighlight[0])
                        pushSpan('constant,equal', partsForHighlight[1])
                        pushSpan('constant,value', partsForHighlight[2][:-1] if partsForHighlight[2].endswith(';') else partsForHighlight[2])
                        pushSpan('', ';')
                    else:
                        errorCount += 1
                        pushSpan('constant,name', constantContent)

                    i = j + (1 if hasSemicolon else 0)

            # gadget #...;
            elif char == '#':
                j = i + 1
                while j < len(line) and line[j] != ';' and line[j] != ' ':
                    j += 1

                hasSemicolon = j < len(line) and line[j] == ';'
                gadgetContent = line[i: j + 1 if hasSemicolon else j]

                if hasSemicolon:
                    gadgetName = gadgetContent[1:-1]
                    allow00 = not gadgetName.startswith('-')
                    if not allow00:
                        gadgetName = gadgetName[1:]

                    # 在 gadgets 列表中查找
                    gadget = None
                    for g in gadgets:
                        if g.get('name') == gadgetName:
                            gadget = g
                            break

                    if gadget is None:
                        errorCount += 1
                        pushSpan('gadget,warning', gadgetContent)
                    else:
                        pushSpan('gadget,closed', gadgetContent)

                        addr = gadget.get('addr', '')
                        hex_str = ''
                        hex_str += addr[3:5] if len(addr) >= 5 else ''
                        if hex_str == '00' and not allow00:
                            hex_str = '01'
                        hex_str += addr[1:3] if len(addr) >= 3 else ''
                        hex_str += f'{"0" if allow00 else "3"}{addr[0] if addr else ""}'
                        hex_str += '00' if allow00 else '30'

                        pushHexChars(hex_str, charPosInInput, lineStartPosInInput + j, 4)
                else:
                    pushSpan('gadget', gadgetContent)

                i = j + (1 if hasSemicolon else 0)

            # 数值块 [...]
            elif char == '[':
                j = i + 1
                while j < len(line) and line[j] != ']':
                    j += 1

                hasBracket = j < len(line) and line[j] == ']'
                valueContent = line[i: j + 1 if hasBracket else j]

                if hasBracket:
                    inner = line[i + 1:j]
                    firstPass = evalExpression(inner, constants, True)
                    value = firstPass['value']
                    hasErrors = firstPass['hasErrors']
                    deferred = firstPass['deferred'] or '$' in inner

                    if hasErrors:
                        errorCount += 1
                        pushSpan('value,closed,warning', valueContent)
                        i = j + 1
                        continue
                    else:
                        pushSpan('value,closed', valueContent)

                    addrStr = f"{value:04X}"
                    littleEndian = addrStr[2:4] + addrStr[0:2]

                    if not deferred:
                        pushHexChars(littleEndian, charPosInInput, lineStartPosInInput + j, 2)
                    else:
                        deferredValuePatches.append({
                            'startHexIndex': len(hexChars),
                            'endHexIndex': len(hexChars),
                            'expression': inner,
                            'startPosInLine': charPosInInput,
                            'endPosInLine': lineStartPosInInput + j,
                            'bytesToInsert': 2
                        })
                        deferredHighlightPatches.append({
                            'lineIndex': lineIndex,
                            'spanIndex': len(spans) - 1,
                            'expression': inner
                        })
                else:
                    pushSpan('value', valueContent)

                i = j + (1 if hasBracket else 0)

            # 地址锚点<-...> 或 <...>
            elif char == '<':
                j = i + 1
                while j < len(line) and line[j] != '>' and line[j] != ' ':
                    j += 1

                hasClose = j < len(line) and line[j] == '>'
                anchorContent = line[i: j + 1 if hasClose else j]

                if hasClose:
                    anchorName = line[i + 1:j]
                    try:
                        addrStart = int(rightStartAddress or '0', 16)
                    except (ValueError, TypeError):
                        addrStart = 0
                    if anchorName.startswith('-'):
                        anchorName = anchorName[1:]
                        try:
                            addrStart = int(leftStartAddress or '0', 16)
                        except (ValueError, TypeError):
                            addrStart = 0

                    if constants.get(anchorName) is not None:
                        errorCount += 1
                        pushSpan('anchor,closed,warning', anchorContent)
                    else:
                        pushSpan('anchor,closed', anchorContent)

                        deferredBytesBeforeAnchor = 0
                        for p in deferredValuePatches:
                            if p['startHexIndex'] <= len(hexChars):
                                deferredBytesBeforeAnchor += p.get('bytesToInsert', 2)

                        addr = addrStart + math.ceil(len(hexChars) / 2) + deferredBytesBeforeAnchor
                        constants[anchorName] = addr
                else:
                    pushSpan('anchor', anchorContent)

                i = j + (1 if hasClose else 0)

            # 十六进制字符和空白块
            elif re.match(r'[0-9a-fA-F]', char):
                j = i + 1
                while j < len(line) and re.match(r'[0-9a-fA-F\s]', line[j]):
                    j += 1

                hexContent = line[i:j]
                pushSpan('hex', hexContent)

                for k in range(i, j):
                    c = line[k]
                    if re.match(r'[0-9a-fA-F]', c):
                        hexChars += c.upper()
                        charPosInInputMap.append(lineStartPosInInput + k)

                i = j

            # 其他字符
            else:
                j = i + 1
                while j < len(line) and not re.match(r'[0-9a-fA-F\/\$#\[<]', line[j]):
                    j += 1
                otherContent = line[i:j]
                pushSpan('other', otherContent)
                i = j

        highlightLines.append(spans)
        posInInput += len(line) + 1

    # 二次阶段：按位置顺序插入延迟字节
    insertedHexCount = 0
    patchesSorted = sorted(deferredValuePatches, key=lambda x: x['startHexIndex'])

    for patch in patchesSorted:
        result = evalExpression(patch['expression'], constants, False)
        if result['hasErrors']:
            errorCount += 1
            continue

        value = result['value']
        addrStr = f"{value:04X}"
        littleEndian = addrStr[2:4] + addrStr[0:2]
        insertPos = patch['startHexIndex'] + insertedHexCount

        hexChars = hexChars[:insertPos] + littleEndian + hexChars[insertPos:]
        insertedHexCount += len(littleEndian)

        if isinstance(charPosInInputMap, list):
            mapping = []
            for _ in range(patch.get('bytesToInsert', 2)):
                mapping.append(patch['startPosInLine'])
                mapping.append(patch['endPosInLine'])
            charPosInInputMap[insertPos:insertPos] = mapping

    # 处理延迟高亮补丁
    for h in deferredHighlightPatches:
        result = evalExpression(h['expression'], constants, False)
        if result['hasErrors']:
            if 0 <= h['lineIndex'] < len(highlightLines) and 0 <= h['spanIndex'] < len(highlightLines[h['lineIndex']]):
                span = highlightLines[h['lineIndex']][h['spanIndex']]
                if span and 'warning' not in span['type']:
                    span['type'] = f"{span['type']},warning"

    return {
        'hexChars': hexChars,
        'charPosInInputMap': charPosInInputMap,
        'highlightLines': highlightLines,
        'errorCount': errorCount
    }

__all__ = [
    'parseRopInput'
]