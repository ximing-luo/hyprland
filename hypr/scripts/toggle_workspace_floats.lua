-- 收起或恢复当前普通工作区及 special:magic 的浮动窗口

local function focus_rank(window)
    return window.focus_history_id >= 0 and window.focus_history_id or math.huge
end

local function most_recent(windows)
    local target = windows[1]
    for _, window in ipairs(windows) do
        if focus_rank(window) < focus_rank(target) then target = window end
    end
    return target
end

local function move_windows(windows, workspace)
    for _, window in ipairs(windows) do
        hl.dispatch(hl.dsp.window.move({ window = window, workspace = workspace, follow = false }))
    end
end

local function toggle_workspace_floats()
    local special = hl.get_active_special_workspace()
    if special and special.name ~= "special:magic" then return end

    if special then
        local windows = special:get_windows()
        local visible_floats = {}
        for _, window in ipairs(windows) do
            if window.mapped and window.floating and not window.pinned then
                table.insert(visible_floats, window)
            end
        end

        local stash = hl.get_workspace("name:__floatstash_magic")
        local stashed_floats = stash and stash:get_windows() or {}

        if #visible_floats > 0 then
            move_windows(visible_floats, "name:__floatstash_magic")
            if #visible_floats == #windows then hl.dispatch(hl.dsp.workspace.toggle_special("magic")) end
            return
        end

        if #stashed_floats == 0 then return end
        local target = most_recent(stashed_floats)
        move_windows(stashed_floats, "special:magic")
        hl.dispatch(hl.dsp.focus({ window = target }))
        return
    end

    local workspace = hl.get_active_workspace()
    if not workspace or workspace.id <= 0 then return end

    local stash_name = "special:floatstash-" .. workspace.id
    local windows = workspace:get_windows()
    local visible_floats = {}
    for _, window in ipairs(windows) do
        if window.mapped and window.floating and not window.pinned then
            table.insert(visible_floats, window)
        end
    end

    local stash = hl.get_workspace(stash_name)
    local stashed_floats = stash and stash:get_windows() or {}

    if #visible_floats > 0 then
        move_windows(visible_floats, stash_name)
        return
    end

    if #stashed_floats == 0 then return end
    local target = most_recent(stashed_floats)
    move_windows(stashed_floats, workspace.id)
    hl.dispatch(hl.dsp.focus({ window = target }))
end

return toggle_workspace_floats
