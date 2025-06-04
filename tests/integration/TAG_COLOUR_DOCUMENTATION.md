# Kanka Tag Colour Field Documentation

## Overview
The `colour` field in Kanka's Tag API has specific requirements that differ from standard web colour formats.

## Valid Colour Formats

### 1. Named Colours (Valid)
The following named colours are accepted by the Kanka API:
- `red`
- `green`
- `yellow`
- `orange`
- `purple`
- `pink`
- `brown`
- `black`
- `grey` (British spelling)
- `navy`
- `teal`
- `aqua`
- `maroon`

### 2. No Colour (Valid)
- Omit the `colour` field entirely
- Use `None` or `null`
- Use an empty string `""`

### 3. Invalid Formats
The following formats are **NOT** accepted and will result in a validation error:
- Hex colours (e.g., `#ff0000`, `ff0000`, `#FF0000`, `FF0000`)
- RGB format (e.g., `rgb(255,0,0)`, `255,0,0`)
- Many standard CSS named colours (e.g., `blue`, `white`, `gray`, `cyan`, `magenta`)
- Numeric indices

## Usage Examples

### Creating a tag with a valid colour:
```python
tag_data = {
    "name": "Important Tag",
    "type": "Category",
    "entry": "<p>This is an important tag.</p>",
    "colour": "red"  # Valid named colour
}
tag = client.tags.create(**tag_data)
```

### Creating a tag without colour:
```python
tag_data = {
    "name": "Normal Tag",
    "type": "Category",
    "entry": "<p>This is a normal tag.</p>"
    # No colour field specified
}
tag = client.tags.create(**tag_data)
```

### Updating a tag's colour:
```python
# Add colour to existing tag
updated_tag = client.tags.update(tag_id, colour="green")

# Remove colour from existing tag
updated_tag = client.tags.update(tag_id, colour="")
```

## Error Handling
When an invalid colour is provided, the API returns:
```json
{
    "code": 422,
    "error": "The selected colour is invalid.",
    "fields": {
        "colour": ["The selected colour is invalid."]
    }
}
```

## Recommendations
1. **Default behavior**: Don't specify the colour field unless specifically needed
2. **Use valid colours only**: Stick to the list of valid named colours above
3. **No hex support**: Don't attempt to use hex colour codes as they are not supported
4. **British spelling**: Use `grey` instead of `gray`